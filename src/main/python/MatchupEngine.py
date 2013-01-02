from math import fabs, floor
from src.main.python.Matchup import Matchup
import numpy.ma as ma

class ReferenceRecord(object):

    def __init__(self, variable_name, value, lat, lon, time, depth):
        self.variable_name = variable_name
        self.value = value
        self.lat = lat
        self.lon = lon
        self.time = time
        self.depth = depth

class MatchupEngine(object):

    def __init__(self, data):
        self.data = data

    def clear_reference_data(self, ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name,
                             ref_time_variable_name, variable_name):
        self.data.clear(ref_lat_variable_name)
        self.data.clear(ref_lon_variable_name)
        self.data.clear(ref_depth_variable_name)
        self.data.clear(ref_time_variable_name)
        self.data.clear(variable_name)

    def find_reference_records(self, variable_name):
        reference_records = []
        if not self.data.has_variable(variable_name):
            return reference_records
        ref_coordinate_variables = self.data.reference_coordinate_variables()
        ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name, ref_depth_variable_name = find_ref_coordinate_names(ref_coordinate_variables)
        self.read_reference_records(ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name, variable_name)
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
        self.clear_reference_data(ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name,
            ref_time_variable_name, variable_name)
        return reference_records

    def find_matchups(self, reference_record, model_variable_name=None, macro_pixel_size=3, max_geographical_delta=50000, max_time_delta=31536000, max_depth_delta=10):
        if model_variable_name is None:
            model_variable_name = reference_record.variable_name
        matchup_positions = self.find_matchup_positions(reference_record.lat, reference_record.lon, macro_pixel_size, max_geographical_delta)
        matchup_times = self.find_matchup_times(reference_record.time, max_time_delta)
        matchup_depths = self.find_matchup_depths(reference_record.depth, max_depth_delta)
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

                    self.data.read(model_variable_name, origin, shape)
                    model_value = self.data[model_variable_name][0]
                    if model_value is ma.masked:
                        continue
                    lon_delta = fabs(matchup_position[2] - reference_record.lon)
                    lat_delta = fabs(matchup_position[3] - reference_record.lat)
                    time_delta = fabs(matchup_time[1] - reference_record.time)
                    matchups.append(Matchup(reference_record.variable_name, model_variable_name, reference_record.value, model_value, reference_record.lat, reference_record.lon, reference_record.time, lat_delta, lon_delta, time_delta, reference_record.depth, depth_delta))

        return matchups

    def find_position(self, dimension, target_value):
        dim_size = self.data.dim_size(dimension)
        self.data.read(dimension, [0], [2])
        first_two_pixels = self.data[dimension]
        pixel_size = first_two_pixels[1] - first_two_pixels[0]
        self.data.clear(dimension)
        return normalise((target_value - first_two_pixels[0]) / pixel_size, dim_size - 1)

    def find_matchup_positions(self, ref_lat, ref_lon, macro_pixel_size, max_geographical_delta):
        offset = int(macro_pixel_size / 2)

        pixel_x = self.find_position('lon', ref_lon)
        pixel_y = self.find_position('lat', ref_lat)

        x_size = self.data.dim_size('lon')
        y_size = self.data.dim_size('lat')

        pixel_positions = []
        min_x = max(pixel_x - offset, 0)
        max_x = min(pixel_x + offset, x_size - 1)
        min_y = max(pixel_y - offset, 0)
        max_y = min(pixel_y + offset, y_size - 1)

        self.data.read('lon', [min_x], [max_x - min_x + 1]) # TODO - move outside!
        self.data.read('lat', [min_y], [max_y - min_y + 1])

        for x in range(0, len(self.data['lon'])):
            current_lon = self.data['lon'][x]
            for y in range(0, len(self.data['lat'])):
                current_lat = self.data['lat'][y]
                if delta(current_lat, current_lon, ref_lat, ref_lon) < max_geographical_delta:
                    pixel_positions.append((x, y, current_lon, current_lat))

        return pixel_positions

    def find_matchup_times(self, ref_time, max_delta):
        return self.find_matchup_indices('time', ref_time, max_delta)

    def find_matchup_depths(self, ref_depth, max_delta):
        if not self.data.has_variable('depth'):
            return [None]
        return self.find_matchup_indices('depth', ref_depth, max_delta)

    def find_matchup_indices(self, dimension, ref, max_delta):
        self.data.read(dimension)
        dimension_data = self.data[dimension]
        index = 0
        matchup_indices = []
        for d in dimension_data:
            if fabs(ref - d) < max_delta:
                matchup_indices.append((index, d))
            index += 1
        return matchup_indices

    def find_all_matchups(self, ref_variable_name, model_variable_name, macro_pixel_size=3, max_geographical_delta=50000, max_time_delta=31536000, max_depth_delta=10):
        reference_records = self.find_reference_records(ref_variable_name)
        all_matchups = []
        for rr in reference_records:
            matchups = self.find_matchups(rr, model_variable_name, macro_pixel_size, max_geographical_delta, max_time_delta, max_depth_delta)
            all_matchups.extend(matchups)
        return all_matchups

    def read_reference_records(self, ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name,
                               ref_time_variable_name, variable_name):
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
    number = int(floor(n + 0.5)) # don't use built-in round because for x.5 it rounds to the next even integer, not to the next higher one
    if number > max:
        return max
    return number

def delta(lat_position, lon_position, lat, lon):
    return pow(lat - lat_position, 2) + pow(lon - lon_position, 2)