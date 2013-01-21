import logging
from math import fabs, floor, sqrt
from opec.Configuration import get_default_config
from opec.Matchup import Matchup

class ReferenceRecord(object):

    def __init__(self, record_number, lat, lon, time, depth):
        self.record_number = record_number
        self.lat = lat
        self.lon = lon
        self.time = time
        self.depth = depth

    def __str__(self):
        return ', '.join('%s: %s' % (k.replace('_ReferenceRecord', ''), vars(self)[k]) for k in vars(self))

class MatchupEngine(object):

    def __init__(self, data, configuration=None):
        self.data = data
        self.config = configuration if configuration is not None else get_default_config()

    def find_all_matchups(self):
        """Finds all matchups
        """
        reference_records = self.find_reference_records()
        all_matchups = []
        for rr in reference_records:
            matchup = self.find_matchup(rr)
            if matchup is not None:
                all_matchups.append(matchup)
        logging.debug('Found %s matchups' % len(all_matchups))
        return all_matchups

    def find_reference_records(self):
        reference_records = []
        ref_coordinate_variables = self.data.reference_coordinate_variables()
        ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name, ref_depth_variable_name = find_ref_coordinate_names(ref_coordinate_variables)
        self.__read_reference_dimensions(ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name)
        for record_number in range(self.data.reference_records_count()):
            ref_lat = self.data[ref_lat_variable_name][record_number]
            ref_lon = self.data[ref_lon_variable_name][record_number]
            ref_time = self.data[ref_time_variable_name][record_number]
            if ref_depth_variable_name is not None:
                ref_depth = self.data[ref_depth_variable_name][record_number]
            else:
                ref_depth = None
            rr = ReferenceRecord(record_number, ref_lat, ref_lon, ref_time, ref_depth)
            reference_records.append(rr)
        logging.debug('Found %s reference records' % (len(reference_records)))
        return reference_records

    def find_matchup(self, reference_record):
        matchup_position = self.find_matchup_position(reference_record.lat, reference_record.lon)
        matchup_time = self.find_matchup_time(reference_record.time)
        matchup_depth = self.__find_matchup_depth(reference_record.depth)
        if None in (matchup_position, matchup_time):
            return None

        cell_position = [matchup_time[0]] # first dimension: time
        spacetime_position = [matchup_time[1]] # first dimension: time
        cell_position.append(matchup_depth[0]) # second dimension: depth
        spacetime_position.append(matchup_depth[1]) # second dimension: depth
        cell_position.append(matchup_position[1]) # third dimension: lat
        spacetime_position.append(matchup_position[3]) # third dimension: lat
        cell_position.append(matchup_position[0]) # fourth dimension: lon
        spacetime_position.append(matchup_position[2]) # fourth dimension: lon

        return Matchup(cell_position, spacetime_position, reference_record)

    def __find_position(self, dimension, target_value):
        dim_size = self.data.dim_size(dimension)
        pixel_size = self.data[dimension][1] - self.data[dimension][0]
        return normalise((target_value - self.data[dimension][0]) / pixel_size, dim_size - 1)

    def find_matchup_position(self, ref_lat, ref_lon):
        self.__prepare_lat_lon_data()

        pixel_x = self.__find_position('lon', ref_lon)
        pixel_y = self.__find_position('lat', ref_lat)

        pixel_position = None

        current_lon = self.data['lon'][pixel_x]
        current_lat = self.data['lat'][pixel_y]

        if delta(current_lat, current_lon, ref_lat, ref_lon) < self.config.geo_delta:
            pixel_position = (pixel_x, pixel_y, current_lon, current_lat)

        return pixel_position

    def __prepare_lat_lon_data(self):
        if not 'lon' in self.data:
            self.data.read('lon')
        if not 'lat' in self.data:
            self.data.read('lat')

    def find_matchup_time(self, ref_time):
        return self.__find_matchup_index('time', ref_time, self.config.time_delta)

    def __find_matchup_depth(self, ref_depth):
        if not self.data.has_variable('depth'):
            return [None, None]
        return self.__find_matchup_index('depth', ref_depth, self.config.depth_delta)

    def __find_matchup_index(self, dimension, ref, max_delta):
        self.data.read(dimension)
        dimension_data = self.data[dimension]
        current_delta = float("inf")
        index = 0
        matchup_index = None
        for d in dimension_data:
            difference = fabs(ref - d)
            if difference < current_delta and difference < max_delta:
                current_delta = difference
                matchup_index = index, d
            index += 1
        return matchup_index

    def __read_reference_dimensions(self, ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name,
                               ref_time_variable_name):
        logging.debug('Reading reference records')
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