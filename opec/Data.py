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

import numpy as np
from opec.NetCDFFacade import NetCDFFacade

class Data(dict):

    def __init__(self, model_file_name, ref_file_name=None):
        super().__init__()
        if ref_file_name is not None:
            self.__reference_file = NetCDFFacade(ref_file_name)
        self.__model_file = NetCDFFacade(model_file_name)
        self.__current_storage = {}

    def model_vars(self):
        return self.__model_file.get_model_variables()

    def close(self):
        self.__model_file.close()
        if self.is_ref_data_split():
            self.__reference_file.close()

    def ref_vars(self):
        ref_vars = self.__model_file.get_reference_variables()
        if self.is_ref_data_split():
            ref_vars.extend(self.__reference_file.get_reference_variables())
        return ref_vars

    def has_model_dimension(self, dimension_name):
        return self.__model_file.has_model_dimension(dimension_name)

    def reference_coordinate_variables(self):
        variables = self.__model_file.get_ref_coordinate_variables()
        if self.is_ref_data_split():
            variables.extend(self.__reference_file.get_ref_coordinate_variables())
        return variables

    def model_dim_size(self, dim_name):
        return self.dim_size(self.__model_file, dim_name)

    def ref_dim_size(self, dim_name):
        if self.is_ref_data_split():
            return self.dim_size(self.__reference_file, dim_name)
        return self.dim_size(self.__model_file, dim_name)

    def dim_size(self, ncfile, dim_name):
        return ncfile.get_dim_size(dim_name)

    def __dimension_string(self, ncfile, variable_name):
        return ncfile.get_dimension_string(variable_name)

    def is_ref_data_split(self):
        return hasattr(self, '_Data__reference_file')

    def reference_records_count(self):
        ref_vars = self.ref_vars()
        if not ref_vars:
            return 0
        if self.is_ref_data_split():
            ncfile = self.__reference_file
        else:
            ncfile = self.__model_file
        return self.dim_size(ncfile, self.__dimension_string(ncfile, ref_vars[0]))

    def read_model(self, variable_name, origin=None, shape=None):
        return self.__read(self.__model_file, variable_name, origin, shape)

    def read_reference(self, variable_name, origin=None, shape=None):
        ncfile = self.__reference_file if self.is_ref_data_split() else self.__model_file
        return self.__read(ncfile, variable_name, origin, shape)

    #todo - allow access to values that have been read, but not exactly the same shape as requested
    def __read(self, ncfile, variable_name, origin=None, shape=None):
        if self.__is_cached(variable_name):
            if self.__can_return_all(origin, shape, variable_name):
                return self[variable_name]
            if origin is not None and shape is not None:
                if self.__current_storage[variable_name] != 'fully_read':
                    current_slice = self.__current_storage[variable_name]
                    # if origin and shape exactly match origin and shape of what has been read before, return that
                    if np.array_equal(origin, current_slice[0]) and np.array_equal(shape, current_slice[1]):
                        return self[variable_name]
        must_fully_read = origin is None and shape is None
        if must_fully_read:
            self[variable_name] = ncfile.get_variable(variable_name)[:]
            self.__current_storage[variable_name] = 'fully_read'
        else:
            self[variable_name] = ncfile.get_data(variable_name, origin, shape)
            self.__current_storage[variable_name] = [np.array(origin), np.array(shape)]
        return self[variable_name]

    def __is_cached(self, variable_name):
        return variable_name in self.__current_storage.keys()

    def __can_return_all(self, origin, shape, variable_name):
        return origin is None and shape is None and self.__current_storage[variable_name] == 'fully_read'

    def unit(self, variable_name):
        is_not_in_ref_file = not self.is_ref_data_split() or self.is_ref_data_split() and self.__reference_file.get_variable(variable_name) is None
        is_not_in_model_file = self.__model_file.get_variable(variable_name) is None
        if is_not_in_model_file and is_not_in_ref_file:
            raise ValueError('Variable \'%s\' not found.' % variable_name)
        if unit(self.__model_file, variable_name):
            return unit(self.__model_file, variable_name)
        if self.is_ref_data_split() and unit(self.__reference_file, variable_name):
            return unit(self.__reference_file, variable_name)
        return None

def unit(ncfile, variable_name):
    if ncfile.get_variable(variable_name):
        return ncfile.get_variable_attribute(variable_name, 'units')
    return None