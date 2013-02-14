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

class ReferenceRecordsFinder(object):

    def __init__(self, data):
        self.data = data

    def find_reference_records(self):
        reference_records = []
        ref_coordinate_variables = self.data.reference_coordinate_variables()
        ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name, ref_depth_variable_name = find_ref_coordinate_names(ref_coordinate_variables)
        self.__read_reference_dimensions(ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name)

        dimension_profiles = []
        for ref_var in self.data.ref_vars():
            dims = {dim for dim in self.data.get_reference_dimensions(ref_var)}
            if dims not in dimension_profiles:
                dimension_profiles.append(dims)
        for dimension_profile in dimension_profiles:
            if len(dimension_profile) == 1:
                self.__find_reference_records_one_dimensional(ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name, dimension_profile, reference_records)
            else:
                self.__find_reference_records_multi_dimensional(ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name, dimension_profile, reference_records)

        return reference_records

    def __read_reference_dimensions(self, ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name,
                                    ref_time_variable_name):
        logging.debug('Reading reference records')
        self.data.read_reference(ref_lat_variable_name)
        self.data.read_reference(ref_lon_variable_name)
        if ref_time_variable_name is not None:
            self.data.read_reference(ref_time_variable_name)
        if ref_depth_variable_name is not None:
            self.data.read_reference(ref_depth_variable_name)

    def __find_reference_records_one_dimensional(self, ref_depth_variable_name, ref_lat_variable_name,
                                               ref_lon_variable_name, ref_time_variable_name, dimension_profile,
                                               reference_records):
        for record_number in range(self.data.ref_dim_size(list(dimension_profile)[0])):
            ref_lat = self.data.__getattribute__(ref_lat_variable_name)[record_number]
            ref_lon = self.data.__getattribute__(ref_lon_variable_name)[record_number]
            # todo - pythonise this by function object or sth
            if ref_time_variable_name is not None:
                ref_time = self.data.__getattribute__(ref_time_variable_name)[record_number]
            else:
                ref_time = None
            if ref_depth_variable_name is not None:
                ref_depth = self.data.__getattribute__(ref_depth_variable_name)[record_number]
            else:
                ref_depth = None
            rr = ReferenceRecord(record_number, ref_lat, ref_lon, ref_time, ref_depth)
            reference_records.append(rr)
        logging.debug('Found %s reference records' % (len(reference_records)))

    def __find_reference_records_multi_dimensional(self, ref_depth_variable_name, ref_lat_variable_name,
                                               ref_lon_variable_name, ref_time_variable_name, dimension_profile,
                                               reference_records):
        lon_index = -1
        depth_index = -1
        time_index = -1
        for record_number in range(self.data.reference_records_count(dimension_profile)):
            lat_index = record_number % len(self.data.__getattribute__(ref_lat_variable_name))
            if lat_index == 0:
                lon_index += 1
                lon_index %= len(self.data.__getattribute__(ref_lon_variable_name))

            ref_lat = self.data.__getattribute__(ref_lat_variable_name)[lat_index]
            ref_lon = self.data.__getattribute__(ref_lon_variable_name)[lon_index]
            if ref_time_variable_name is not None:
                if lat_index == 0 and lon_index == 0:
                    time_index += 1 % len(self.data.__getattribute__(ref_time_variable_name))
                ref_time = self.data.__getattribute__(ref_time_variable_name)[time_index]
            else:
                ref_time = None
            if ref_depth_variable_name is not None:
                if lat_index == 0 and lon_index == 0 and time_index == 0:
                    depth_index += 1 % len(self.data.__getattribute__(ref_depth_variable_name))
                ref_depth = self.data.__getattribute__(ref_depth_variable_name)[depth_index]
            else:
                ref_depth = None
            rr = ReferenceRecord(record_number, ref_lat, ref_lon, ref_time, ref_depth)
            reference_records.append(rr)
        logging.debug('Found %s reference records' % (len(reference_records)))

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

class ReferenceRecord(object):

    def __init__(self, record_number, lat, lon, time, depth):
        self.record_number = record_number
        self.lat = lat
        self.lon = lon
        self.time = time
        self.depth = depth

    def __str__(self):
        return ', '.join('%s: %s' % (k.replace('_ReferenceRecord', ''), vars(self)[k]) for k in vars(self))