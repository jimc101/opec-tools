# Copyright (C) 2013 Brockmann Consult GmbH (info@brockmann-consult.de)
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see http://www.gnu.org/licenses/gpl.html

import logging
from math import fabs, floor

from opec.Configuration import get_default_config
from opec.Matchup import Matchup
from opec.ReferenceRecordsFinder import ReferenceRecordsFinder


class MatchupEngine(object):

    def __init__(self, data, configuration=None):
        self.data = data
        self.config = configuration if configuration is not None else get_default_config()
        self.pixel_sizes = {}

    def find_all_matchups(self):
        rrf = ReferenceRecordsFinder(self.data)
        reference_records = rrf.find_reference_records()
        index = 0
        all_matchups = []
        for rr in reference_records:
            index += 1
            matchups = self.find_matchups(rr)
            if index % 1000 == 0:
                logging.debug('Found matchups for %s reference records so far' % index)
                logging.debug('Found %s matchups so far' % len(all_matchups))
            if matchups:
                all_matchups.extend(matchups)

        logging.debug('Found %s matchups' % len(all_matchups))
        return all_matchups

    def find_matchups(self, reference_record):
        matchup_position = self.find_matchup_position(reference_record.lat, reference_record.lon)
        matchup_times = self.find_matchup_times(reference_record.time)
        matchup_depths = self.__find_matchup_depths(reference_record.depth)

        matchups = []
        for matchup_time in matchup_times:
            for matchup_depth in matchup_depths:
                cell_position = [matchup_time[0]] # first dimension: time
                spacetime_position = [matchup_time[1]] # first dimension: time
                cell_position.append(matchup_depth[0]) # second dimension: depth
                spacetime_position.append(matchup_depth[1]) # second dimension: depth
                cell_position.append(matchup_position[1]) # third dimension: lat
                spacetime_position.append(matchup_position[3]) # third dimension: lat
                cell_position.append(matchup_position[0]) # fourth dimension: lon
                spacetime_position.append(matchup_position[2]) # fourth dimension: lon
                matchups.append(Matchup(cell_position, spacetime_position, reference_record))

        return matchups

    def __find_position(self, dimension, target_value):
        dim_size = self.data.model_dim_size(dimension)
        if dimension in self.pixel_sizes:
            pixel_size = self.pixel_sizes[dimension]
        else:
            self.__prepare_lat_lon_data()
            pixel_size = self.data.__getattribute__(dimension)[1] - self.data.__getattribute__(dimension)[0]
        return normalise((target_value - self.data.__getattribute__(dimension)[0]) / pixel_size, dim_size - 1)

    def find_matchup_position(self, ref_lat, ref_lon):
        lon_variable_name = self.data.find_model_longitude_variable_name()
        lat_variable_name = self.data.find_model_latitude_variable_name()

        pixel_x = self.__find_position(lon_variable_name, ref_lon)
        pixel_y = self.__find_position(lat_variable_name, ref_lat)

        current_lon = self.data.__getattribute__(lon_variable_name)[pixel_x]
        current_lat = self.data.__getattribute__(lat_variable_name)[pixel_y]

        return (pixel_x, pixel_y, current_lon, current_lat)

    def __prepare_lat_lon_data(self):
        self.data.read_model(self.data.find_model_latitude_variable_name())
        self.data.read_model(self.data.find_model_longitude_variable_name())

    def find_matchup_times(self, ref_time):
        return self.__find_matchup_index(ref_time, 'time', self.config.time_delta)

    def __find_matchup_depths(self, ref_depth):
        return self.__find_matchup_index(ref_depth, 'depth', self.config.depth_delta)

    def __find_matchup_index(self, ref_value, name, delta):
        if not self.data.has_model_dimension(name):
            return [[None, None]]
        if ref_value is None:
            return self.get_all_indices(name)
        matchup_index = self.__find_matchup_index_in_model_data(name, ref_value, delta)
        if matchup_index is not None:
            return [matchup_index]
        else:
            return []

    def get_all_indices(self, coordinate_variable_name):
        if not hasattr(self, 'indices'):
            self.indices = {}
        if coordinate_variable_name in self.indices:
            return self.indices[coordinate_variable_name]
        indices = []
        self.data.read_model(coordinate_variable_name)
        dimension_data = self.data.__getattribute__(coordinate_variable_name)
        index = 0
        for d in dimension_data:
            indices.append((index, d))
            index += 1
        self.indices[coordinate_variable_name] = indices
        return indices

    def __find_matchup_index_in_model_data(self, dimension, ref, max_delta):
        self.data.read_model(dimension)
        dimension_data = self.data.__getattribute__(dimension)
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


def normalise(n, max):
    # don't use built-in round because for x.5 it rounds to the next even integer, not to the next higher one
    # example: round(2.5) -> 2, round(3.5) -> 4
    # instead, use more linear method
    number = int(floor(n + 0.5))
    if number > max:
        return max
    return number