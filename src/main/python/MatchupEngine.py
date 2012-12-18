from math import fabs
from src.main.python.Matchup import Matchup

class ReferenceRecord(object):

    def __init__(self, variable_name, value, lat, lon, time, depth):
        self.variable_name = variable_name
        self.value = value
        self.lat = lat
        self.lon = lon
        self.time = time
        self.depth = depth

class MatchupEngine(object):

    def __init__(self, netcdf):
        self.netcdf = netcdf

    def find_reference_records(self, variable_name):
        reference_records = []
        if not self.netcdf.has_variable(variable_name):
            return reference_records
        ref_coordinate_variables = self.netcdf.get_ref_coordinate_variables()
        ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name, ref_depth_variable_name = find_ref_coordinate_names(ref_coordinate_variables)
        for i in range(self.netcdf.get_dim_size(self.netcdf.get_dimension_string(variable_name))):
            ref_value = self.netcdf.get_data(variable_name, [i], [1])
            ref_lat = self.netcdf.get_data(ref_lat_variable_name, [i], [1])
            ref_lon = self.netcdf.get_data(ref_lon_variable_name, [i], [1])
            ref_time = self.netcdf.get_data(ref_time_variable_name, [i], [1])
            if ref_depth_variable_name is not None:
                ref_depth = self.netcdf.get_data(ref_depth_variable_name, [i], [1])
            else:
                ref_depth = None
            rr = ReferenceRecord(variable_name, ref_value, ref_lat, ref_lon, ref_time, ref_depth)
            reference_records.append(rr)
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

                    lon_delta = fabs(matchup_position[2] - reference_record.lon)
                    lat_delta = fabs(matchup_position[3] - reference_record.lat)
                    time_delta = fabs(matchup_time[1] - reference_record.time)
                    model_value = self.netcdf.get_data(model_variable_name, origin, shape)[0]
                    matchups.append(Matchup(reference_record.variable_name, model_variable_name, reference_record.value, model_value, reference_record.lat, reference_record.lon, reference_record.time, lat_delta, lon_delta, time_delta, reference_record.depth, depth_delta))

        return matchups

    def find_position(self, dimension, target_value):
        dim_size = self.netcdf.get_dim_size(dimension)
        first_two_pixels = self.netcdf.get_data(dimension, [0], [2])
        pixel_size = first_two_pixels[1] - first_two_pixels[0]
        return normalise((target_value - first_two_pixels[0]) / pixel_size, dim_size - 1)

    def find_matchup_positions(self, ref_lat, ref_lon, macro_pixel_size, max_geographical_delta):
        offset = int(macro_pixel_size / 2)

        pixel_x = self.find_position('lon', ref_lon)
        pixel_y = self.find_position('lat', ref_lat)

        x_size = self.netcdf.get_dim_size('lon')
        y_size = self.netcdf.get_dim_size('lat')

        pixel_positions = []
        min_x = max(pixel_x - offset, 0)
        max_x = min(pixel_x + offset, x_size - 1) + 1
        min_y = max(pixel_y - offset, 0)
        max_y = min(pixel_y + offset, y_size - 1) + 1
        for x in range(min_x, max_x):
            current_lon = self.netcdf.get_data('lon', [x], [1])[0]
            for y in range(min_y, max_y):
                current_lat = self.netcdf.get_data('lat', [y], [1])[0]
                if self.delta(current_lat, current_lon, ref_lat, ref_lon) < max_geographical_delta:
                    pixel_positions.append((x, y, current_lon, current_lat))

        return pixel_positions

    def delta(self, lat_position, lon_position, lat, lon):
        return pow(lat - lat_position, 2) + pow(lon - lon_position, 2)

    def find_matchup_times(self, ref_time, max_delta):
        return self.find_matchup_indices('time', ref_time, max_delta)

    def find_matchup_depths(self, ref_depth, max_delta):
        if self.netcdf.get_variable('depth') is None:
            return [None]
        return self.find_matchup_indices('depth', ref_depth, max_delta)

    def find_matchup_indices(self, dim, ref, max_delta):
        data = self.netcdf.read_variable_fully(dim)
        index = 0
        matchup_indices = []
        for d in data:
            if fabs(ref - d) < max_delta:
                matchup_indices.append((index, d))
            index += 1
        return matchup_indices

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
    number = int(fabs(n))
    if number > max:
        return max
    return number