import logging
from math import fabs, floor, sqrt
from opec.Configuration import get_default_config
import numpy.ma as ma
from opec.Matchup import Matchup

class ReferenceRecord(object):

    def __init__(self, variable_name, value, lat, lon, time, depth):
        self.variable_name = variable_name
        self.value = value
        self.lat = lat
        self.lon = lon
        self.time = time
        self.depth = depth

class MatchupEngine(object):

    def __init__(self, data, configuration=None):
        self.data = data
        self.config = configuration if configuration is not None else get_default_config()

    def find_all_matchups(self, ref_variable_name, model_variable_name):
        """Finds all matchups between the given reference variable and model variable.
        """
        reference_records = self.find_reference_records(ref_variable_name)
        all_matchups = []
        for rr in reference_records:
            matchups = self.find_matchups(rr, model_variable_name)
            all_matchups.extend(matchups)
        logging.debug('Found %s matchups between \'%s\' and \'%s\'.' % (len(all_matchups), model_variable_name, ref_variable_name))
        return all_matchups

    def find_reference_records(self, variable_name):
        reference_records = []
        if not self.data.has_variable(variable_name):
            logging.debug('No reference records for variable \'%s\' found.' % variable_name)
            return reference_records
        ref_coordinate_variables = self.data.reference_coordinate_variables()
        ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name, ref_depth_variable_name = find_ref_coordinate_names(ref_coordinate_variables)
        self.__read_reference_records(ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name, variable_name)
        for i in range(self.data.reference_records_count()):
            ref_value = self.data[variable_name][i]
            if ref_value is ma.masked:
                continue
            ref_lat = self.data[ref_lat_variable_name][i]
            ref_lon = self.data[ref_lon_variable_name][i]
            ref_time = self.data[ref_time_variable_name][i]
            if ref_depth_variable_name is not None:
                ref_depth = self.data[ref_depth_variable_name][i]
            else:
                ref_depth = None
            rr = ReferenceRecord(variable_name, ref_value, ref_lat, ref_lon, ref_time, ref_depth)
            reference_records.append(rr)
        logging.debug('Found %s reference records for variable \'%s\'.' % (len(reference_records), variable_name))
        return reference_records

    def find_matchups(self, reference_record, model_variable_name=None):
        if model_variable_name is None:
            model_variable_name = reference_record.variable_name
        matchup_positions = self.find_matchup_positions(reference_record.lat, reference_record.lon)
        matchup_times = self.find_matchup_times(reference_record.time)
        matchup_depths = self.__find_matchup_depths(reference_record.depth)
        matchups = []
        for matchup_position in matchup_positions:
            for matchup_time in matchup_times:
                for matchup_depth in matchup_depths:
                    shape = [1, 1, 1]
                    origin = [matchup_time[0]] # first dimension: time
                    depth_delta = None
                    if matchup_depth is not None:
                        origin.append(matchup_depth[0]) # second dimension: depth (if existing)
                        shape.append(1)
                        depth_delta = fabs(matchup_depth[1] - reference_record.depth)
                    origin.append(matchup_position[1]) # second or third dimension: lat
                    origin.append(matchup_position[0]) # third or fourth dimension: lon

                    self.data.read(model_variable_name, origin, shape) # TODO: here, only a single is pixel is read. Pull this outside!
                    model_value = self.data[model_variable_name].reshape(1)[0]
                    if model_value is ma.masked:
                        continue
                    lon_delta = fabs(matchup_position[2] - reference_record.lon)
                    lat_delta = fabs(matchup_position[3] - reference_record.lat)
                    time_delta = fabs(matchup_time[1] - reference_record.time)
                    matchups.append(Matchup(reference_record.variable_name, model_variable_name, reference_record.value, model_value, reference_record.lat, reference_record.lon, reference_record.time, lat_delta, lon_delta, time_delta, reference_record.depth, depth_delta))
        return matchups

    def __find_position(self, dimension, target_value):
        dim_size = self.data.dim_size(dimension)
        pixel_size = self.data[dimension][1] - self.data[dimension][0]
        return normalise((target_value - self.data[dimension][0]) / pixel_size, dim_size - 1)

    def find_matchup_positions(self, ref_lat, ref_lon):
        self.__prepare_lat_lon_data()
        offset = int(self.config.macro_pixel_size / 2)

        pixel_x = self.__find_position('lon', ref_lon)
        pixel_y = self.__find_position('lat', ref_lat)

        x_size = self.data.dim_size('lon')
        y_size = self.data.dim_size('lat')

        pixel_positions = []
        min_x = max(pixel_x - offset, 0)
        max_x = min(pixel_x + offset, x_size - 1)
        min_y = max(pixel_y - offset, 0)
        max_y = min(pixel_y + offset, y_size - 1)

        for x in range(min_x, max_x + 1):
            current_lon = self.data['lon'][x]
            for y in range(min_y, max_y + 1):
                current_lat = self.data['lat'][y]
                if delta(current_lat, current_lon, ref_lat, ref_lon) < self.config.geo_delta:
                    pixel_positions.append((x, y, current_lon, current_lat))

        return pixel_positions

    def __prepare_lat_lon_data(self):
        if not 'lon' in self.data:
            self.data.read('lon')
        if not 'lat' in self.data:
            self.data.read('lat')

    def find_matchup_times(self, ref_time):
        return self.__find_matchup_indices('time', ref_time, self.config.time_delta)

    def __find_matchup_depths(self, ref_depth):
        if not self.data.has_variable('depth'):
            return [None]
        return self.__find_matchup_indices('depth', ref_depth, self.config.depth_delta)

    def __find_matchup_indices(self, dimension, ref, max_delta):
        self.data.read(dimension)
        dimension_data = self.data[dimension]
        index = 0
        matchup_indices = []
        for d in dimension_data:
            if fabs(ref - d) < max_delta:
                matchup_indices.append((index, d))
            index += 1
        return matchup_indices

    def __read_reference_records(self, ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name,
                               ref_time_variable_name, variable_name):
        logging.debug('Reading reference records')
        self.data.read(variable_name)
        self.data.read(ref_lat_variable_name)
        self.data.read(ref_lon_variable_name)
        self.data.read(ref_time_variable_name)
        if ref_depth_variable_name is not None:
            self.data.read(ref_depth_variable_name)

def find_ref_coordinate_names(ref_coordinate_variables):
    lat = None
    lon = None
    time = None
    depth = None

    for var in ref_coordinate_variables:
        if 'lat' in var:
            lat = var
        if 'lon' in var:
            lon = var
        if 'time' in var:
            time = var
        if 'depth' in var:
            depth = var

    return lat, lon, time, depth

def normalise(n, max):
    # don't use built-in round because for x.5 it rounds to the next even integer, not to the next higher one
    # example: round(2.5) -> 2, round(3.5) -> 4
    # instead, use more linear method
    number = int(floor(n + 0.5))
    if number > max:
        return max
    return number

def delta(lat_position, lon_position, lat, lon):
    # returns the euclidean distance; sufficient here
    return sqrt(pow(lat - lat_position, 2) + pow(lon - lon_position, 2))