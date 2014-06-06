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
import functools
import logging
import sys
import os
import numpy.ma as ma

from opec import utils
from opec.netCDF_facade import NetCDFFacade

class Data(object):

    def __init__(self, model_file_name, ref_file_name=None, max_cache_size=None):
        if ref_file_name is not None:
            self.__reference_file = NetCDFFacade(ref_file_name)
        if model_file_name is not None:
            self.__model_file = NetCDFFacade(model_file_name)
        self.max_cache_size = max_cache_size if max_cache_size is not None else sys.maxsize
        self.cached_list = []
        self.current_memory = 0


    def model_vars(self):
        if not hasattr(self, 'model_variables'):
            self.model_variables = self.__model_file.get_model_variables()
        return self.model_variables


    def close(self):
        self.__model_file.close()
        if self.is_ref_data_split():
            self.__reference_file.close()


    def ref_vars(self):
        if hasattr(self, 'reference_variables'):
            return self.reference_variables
        reference_variables = self.__model_file.get_reference_variables()
        if self.is_ref_data_split():
            reference_variables.extend(self.__reference_file.get_reference_variables())
        self.reference_variables = reference_variables
        return reference_variables


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


    def reference_records_count(self, dimension_profile):
        ref_vars = self.ref_vars()
        if not ref_vars:
            return 0
        if self.is_ref_data_split():
            ncfile = self.__reference_file
        else:
            ncfile = self.__model_file

        dim_size = 0
        for var in ref_vars:
            dimensions = self.__dimension_string(ncfile, var).split(' ')
            dimension_set = {x for x in dimensions}
            if dimension_profile == dimension_set:
                temp = 1
                for dim in dimension_profile:
                    temp *= self.dim_size(ncfile, dim)
                dim_size += temp
        return dim_size


    def get_reference_dimensions(self, variable_name=None):
        if self.is_ref_data_split():
            ncfile = self.__reference_file
        else:
            ncfile = self.__model_file
        return ncfile.get_dimensions(variable_name)


    def get_model_dimensions(self, variable_name=None):
        if not hasattr(self, 'model_dimensions'):
            self.model_dimensions = {}
        if not variable_name in self.model_dimensions:
            self.model_dimensions[variable_name] = self.__model_file.get_dimensions(variable_name)
        return self.model_dimensions[variable_name]


    def read_model(self, variable_name, origin=None):
        return self.__read(self.__model_file, variable_name, origin)


    def read_reference(self, variable_name, origin=None):
        ncfile = self.__reference_file if self.is_ref_data_split() else self.__model_file
        return self.__read(ncfile, variable_name, origin)


    def find_item_to_delete(self):
        self.cached_list = sorted(self.cached_list, key=self.compute_variable_size, reverse=True)
        return self.cached_list.pop(0)


    def get_current_cache_size(self):
        return sum([self.compute_variable_size(variable_name) for variable_name in self.cached_list])


    def ensure_memory(self, variable_size):
        will_cache_overflow = self.max_cache_size <= self.current_memory + variable_size
        while will_cache_overflow and len(self.cached_list) > 0:
            var_to_delete = self.find_item_to_delete()
            self.current_memory -= self.compute_variable_size(var_to_delete)
            logging.debug('Deleting variable \'%s\' from cache.' % var_to_delete)
            self.__delattr__(var_to_delete)
            will_cache_overflow = self.max_cache_size <= self.current_memory + variable_size
        if not os.name == 'nt':
            logging.debug('Memory in use after \'ensure_memory\' called: %.2f MB' % (mem() / 1024))


    def __read(self, ncfile, variable_name, origin=None):
        variable_size = self.compute_variable_size(variable_name)
        if not self.__is_cached(variable_name):
            self.ensure_memory(variable_size)
            logging.debug('Reading variable \'%s\' fully into cache.' % variable_name)
            if not os.name == 'nt':
                logging.debug('Memory in use before reading variable %s fully into cache: %.2f MB' % (variable_name, mem() / 1024))
            variable = ncfile.get_variable(variable_name)
            self.__setattr__(variable_name, variable[:])
            self.cached_list.append(variable_name)
            self.current_memory += self.compute_variable_size(variable_name)
            if not os.name == 'nt':
                logging.debug('Memory in use after reading variable %s fully into cache: %.2f MB' % (variable_name, mem() / 1024))
        if origin is None:
            return ma.array(self.__getattribute__(variable_name))

        return self.get_data(origin, variable_name)


    def get_data(self, origin, variable_name):
        '''
        Read single pixel from origin
        '''

        return self.__getattribute__(variable_name)[tuple(origin)]


    def __is_cached(self, variable_name):
        return variable_name in self.cached_list


    def __find_model_variable_name(self, possible_names, standard_name):
        for name in possible_names:
            if self.__model_file.get_variable(name) is not None:
                return name
        for var in self.__model_file.get_coordinate_variables():
            if self.__model_file.attribute(var.name, 'standard_name') == standard_name:
                return var.name
        raise ValueError('Unable to find \'%s\'-variable.' % standard_name)


    def find_model_latitude_variable_name(self):
        return self.__find_model_variable_name(['lat', 'latitude'], 'latitude')


    def find_model_longitude_variable_name(self):
        return self.__find_model_variable_name(['lon', 'longitude'], 'longitude')


    def unit(self, variable_name):
        is_not_in_ref_file = not self.is_ref_data_split() or self.is_ref_data_split() and self.__reference_file.get_variable(variable_name) is None
        is_not_in_model_file = self.__model_file.get_variable(variable_name) is None
        if is_not_in_model_file and is_not_in_ref_file:
            raise ValueError('Variable \'%s\' not found.' % variable_name)
        model_unit = utils.get_unit(self.__model_file, variable_name)
        if model_unit:
            return model_unit
        if self.is_ref_data_split() and utils.get_unit(self.__reference_file, variable_name):
            return utils.get_unit(self.__reference_file, variable_name)
        return None


    def compute_variable_size(self, variable_name):
        variable = self.__model_file.get_variable(variable_name)
        if variable is None and self.is_ref_data_split():
            variable = self.__reference_file.get_variable(variable_name)
        if variable is None:
            raise ValueError('No variable found with name \'%s\'' % variable_name)
        return compute_array_size(variable.shape, variable.dtype.itemsize)


    def has_one_dim_ref_var(self):
        for var in self.ref_vars():
            if len(self.get_reference_dimensions(var)) == 1:
                return True
        return False


    def get_values(self, ref_name, model_name):
        model_values_slices, ref_values_slices = self.get_slices(model_name, ref_name)

        model_values = self.read_model(model_name)[model_values_slices]
        reference_values = self.read_reference(ref_name)[ref_values_slices]
        reference_values.mask = reference_values.mask | model_values.mask
        model_values.mask = reference_values.mask | model_values.mask

        logging.debug('Compressing ref-variable %s' % ref_name)
        reference_values = reference_values.compressed()

        logging.debug('Compressing model variable %s' % model_name)
        model_values = model_values.compressed()

        return reference_values, model_values


    def get_slices(self, model_name, ref_name):
        differing_dim_names = self.get_differing_dim_names(model_name, ref_name)
        differing_model_dimension_var_indices = self.__get_differing_model_dimension_var_indices(differing_dim_names)
        model_values_slices = []
        for dim in self.get_model_dimensions(model_name):
            if dim in differing_dim_names.keys():
                index = differing_model_dimension_var_indices[dim]
                model_values_slices.append(slice(index, index + 1))
            else:
                model_values_slices.append(slice(None))
        ref_values_slices = []
        for dim in self.get_reference_dimensions(ref_name):
            if dim in differing_dim_names.values():
                ref_values_slices.append(slice(0, 1))
            else:
                ref_values_slices.append(slice(0, self.ref_dim_size(dim)))
        return model_values_slices, ref_values_slices


    def get_differing_dim_names(self, model_var, ref_var):
        dim_names = {}
        model_dims = self.__dimension_string(self.__model_file, model_var)
        ref_file = self.__reference_file if self.is_ref_data_split() else self.__model_file
        ref_dims = self.__dimension_string(ref_file, ref_var)
        if model_dims == ref_dims:
            return dim_names
        model_dims_list = model_dims.split(' ')
        ref_dims_list = ref_dims.split(' ')
        if not len(model_dims_list) == len(ref_dims_list):
            raise ValueError('model and gridded ref variable need to have identical dimension count')
        for index, model_dim in enumerate(model_dims_list):
            ref_dim = ref_dims_list[index]
            if not ref_dim == model_dim:
                dim_names[model_dim] = ref_dim
        return dim_names


    def __get_differing_model_dimension_var_indices(self, differing_dim_names):
        differing_model_dimension_var_indices = {}
        for differing_dim in differing_dim_names.keys():
            differing_model_dim = differing_dim
            differing_ref_dim = differing_dim_names[differing_dim]
            differing_dim_model_values = self.read_model(differing_model_dim)
            # we're assuming here that such differing dimensions for ref data have only a single value
            differing_dim_ref_value = self.read_reference(differing_ref_dim, (0, ))
            dim_var_index = self.__get_dimension_var_index(differing_dim_model_values, differing_dim_ref_value)
            differing_model_dimension_var_indices[differing_model_dim] = dim_var_index

        return differing_model_dimension_var_indices


    def __get_dimension_var_index(self, dim_values, ref_value):
        # find out grid position where differing dimension variables are nearest
        min_delta = float('inf')
        index = -1
        for loop_index, model_dim_value in enumerate(dim_values):
            current_delta = abs(model_dim_value - ref_value)
            if current_delta < min_delta:
                min_delta = current_delta
                index = loop_index

        return index


def compute_array_size(shape, itemsize):
    num_entries = functools.reduce(lambda x, y: x * y, shape)
    byte_size = num_entries * itemsize
    return byte_size / (1024 * 1024)


def mem():
    return int(os.popen('ps -p %d -o rss | tail -1' % os.getpid()).read())
