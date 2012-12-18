from math import fabs
from src.main.python.Matchup import Matchup

class ReferenceRecord(object):

    def __init__(self, variable_name, value, lat, lon, time, depth=None):
        self.variable_name = variable_name
        self.value = value
        self.lat = lat
        self.lon = lon
        self.time = time
        self.depth = depth

class MatchupEngine(object):

    def __init__(self, netcdf):
        self.netcdf = netcdf

    def find_matchups(self, reference_record, macro_pixel_size=3, max_geographical_delta=50000, max_time_delta=31536000, max_depth_delta=10):
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
                    origin.append(matchup_position[1]) # third dimension: lat
                    origin.append(matchup_position[0]) # fourth dimension: lon

                    lon_delta = fabs(matchup_position[2] - reference_record.lon)
                    lat_delta = fabs(matchup_position[3] - reference_record.lat)
                    time_delta = fabs(matchup_time[1] - reference_record.time)
                    model_value = self.netcdf.get_data(reference_record.variable_name, origin, shape)[0]
                    matchups.append(Matchup(reference_record.variable_name, reference_record.value, model_value, reference_record.lat, reference_record.lon, reference_record.time, lat_delta, lon_delta, time_delta, reference_record.depth, depth_delta))

        return matchups

    def normalise(self, n, max):
        number = int(fabs(n))
        if number > max:
            return max
        return number

    def delta(self, lat_position, lon_position, lat, lon):
        return pow(lat - lat_position, 2) + pow(lon - lon_position, 2)

    def find_position(self, dimension, target):
        dim_size = self.netcdf.get_dim_size(dimension)
        first_two_pixels = self.netcdf.get_data(dimension, [0], [2])
        pixel_size = first_two_pixels[1] - first_two_pixels[0]
        target_pixel = self.normalise((target - first_two_pixels[0]) / pixel_size, dim_size - 1)
        return target_pixel

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

    def find_matchup_times(self, time, max_delta):
        time_data = self.netcdf.read_variable_fully('time')
        index = 0
        matchup_times = []
        for t in time_data:
            if fabs(time - t) < max_delta:
                matchup_times.append((index, t))
            index += 1
        return matchup_times

    def find_matchup_depths(self, depth, max_delta):
        if self.netcdf.get_variable('depth') is None:
            return [None]
        depth_data = self.netcdf.read_variable_fully('depth')
        index = 0
        matchup_depths = []
        for t in depth_data:
            if fabs(depth - t) < max_delta:
                matchup_depths.append((index, t))
            index += 1
        return matchup_depths
