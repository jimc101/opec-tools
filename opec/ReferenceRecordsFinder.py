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
        ref_coordinate_variables = self.data.reference_coordinate_variables()
        ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name, ref_depth_variable_name = find_ref_coordinate_names(ref_coordinate_variables)
        self.__read_reference_dimensions(ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name)

        for ref_var in self.data.ref_vars():
            dimensions = self.data.get_reference_dimensions(ref_var)
            if len(dimensions) > 1:
                continue
            dim_size = self.data.ref_dim_size(dimensions[0])
            return self.__find_reference_records(dim_size, ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name)
        return []

    def __read_reference_dimensions(self, ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name,
                                    ref_time_variable_name):
        logging.debug('Reading reference records')
        self.data.read_reference(ref_lat_variable_name)
        self.data.read_reference(ref_lon_variable_name)
        if ref_time_variable_name is not None:
            self.data.read_reference(ref_time_variable_name)
        if ref_depth_variable_name is not None:
            self.data.read_reference(ref_depth_variable_name)

    def __find_reference_records(self, dim_size, ref_depth_variable_name, ref_lat_variable_name, ref_lon_variable_name, ref_time_variable_name):
        reference_records = []
        for record_number in range(dim_size):
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
        return reference_records


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