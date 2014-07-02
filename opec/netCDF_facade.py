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
from netCDF4 import Dataset

class NetCDFFacade(object):

    def __init__(self, filename=None, dataset=None):
        if filename is not None:
            try:
                self.data_set = Dataset(filename, 'r', format='NETCDF4_CLASSIC')
            except RuntimeError as re:
                raise ValueError('%s: %s' % (re.args[0], filename))
        elif dataset is not None:
            self.data_set = dataset
        else:
            raise ValueError('Either filename or dataset must be provided')


    def get_dim_size(self, dimName):
        dimensions = self.data_set.dimensions
        for currentDimName in dimensions:
            if currentDimName == dimName:
                return len(dimensions[currentDimName])


    def get_global_attribute(self, attributeName):
        globalAttributes = self.data_set.ncattrs
        for currentAttribute in globalAttributes():
            if currentAttribute == attributeName:
                return self.data_set.__getattribute__(attributeName)


    def get_variable(self, variableName):
        variables = self.data_set.variables
        for currentVarName in variables:
            if currentVarName == variableName:
                return variables[currentVarName]
        return None


    def get_variable_attribute(self, variableName, attributeName):
        variable = self.get_variable(variableName)
        if hasattr(variable, attributeName):
            return variable.__getattribute__(attributeName)
        return None


    def get_dimension_string(self, variableName):
        variable = self.get_variable(variableName)
        dimensionString = ""
        for dimName in variable._getdims():
            dimensionString = "%s%s " % (dimensionString, dimName)
        dimensionString = dimensionString.strip()
        return dimensionString


    def get_dim_length(self, variableName, index=0):
        variable = self.get_variable(variableName)
        variableDimensions = variable._getdims()
        for i in range(len(variableDimensions)):
            if i == index:
                dimName = variableDimensions[i]
                return self.get_dim_size(dimName)


    def get_data(self, variableName, origin, shape):
        variable = self.get_variable(variableName)
        dimCount = len(variable._getdims())
        if dimCount != len(origin) or dimCount != len(shape):
            raise ValueError("len(origin) and len(shape) must be equal to number of dimensions of variable '" + variableName + "'")
        index_array = []
        for dimIndex in range(0, dimCount):
            current_index = range(origin[dimIndex], origin[dimIndex] + shape[dimIndex])
            index_array.append(current_index)
        # ensure that resulting array has same dimension as variable
        # unfortunately, the netcdf lib reduces the array's rank in some cases
        array = variable[index_array]
        if len(array.shape) < len(variable._getdims()):
            new_shape = []
            for d in range(dimCount - len(array.shape)):
                new_shape.append(1)
            for i in array.shape:
                new_shape.append(i)
            array = array.reshape(new_shape)
        return array


    def close(self):
        self.data_set.close()


    def get_dimensions(self, variable_name=None):
        result = []
        if variable_name is None:
            for dimension in self.data_set.dimensions:
                result.append(dimension)
            return result
        return (self.get_variable(variable_name))._getdims()


    def is_coordinate_or_reference_variable(self, ncVariable):
        return len(ncVariable._getdims()) == 1


    def get_model_variables(self):
        result = []
        for variable_name in self.data_set.variables:
            nc_variable = self.get_variable(variable_name)
            if not self.is_coordinate_or_reference_variable(nc_variable) and not self.is_reference_variable(nc_variable):
                result.append(variable_name)
        return result


    def read_variable_fully(self, variableName):
        return self.get_variable(variableName)


    def get_variable_size(self, variableName):
        shape = self.data_set.variables[variableName].shape
        return functools.reduce(lambda x, y: x * y, shape)


    def is_reference_variable(self, nc_variable):
        is_one_dimensional_reference_variable = self.is_coordinate_or_reference_variable(nc_variable) and self.has_coordinates_attribute(nc_variable)
        return is_one_dimensional_reference_variable or self.attribute(nc_variable._name, 'is_reference')


    def is_coordinate_variable(self, ncVariable):
        return self.is_coordinate_or_reference_variable(ncVariable) and not self.has_coordinates_attribute(ncVariable)


    def get_reference_variables(self):
        result = []
        for variableName in self.data_set.variables:
            nc_variable = self.get_variable(variableName)
            if self.is_reference_variable(nc_variable):
                result.append(variableName)
        return result


    def get_reference_variable(self, variable_name):
        nc_variable = self.get_variable(variable_name)
        if nc_variable is None or not self.is_reference_variable(nc_variable):
            return None
        return nc_variable


    def has_coordinates_attribute(self, ncVariable):
        for attribute in ncVariable.ncattrs():
            if str(attribute) == 'coordinates':
                return True
        return False


    def get_coordinate_variables(self):
        result = []
        for var in self.data_set.variables:
            dimensionStringIsVarName = self.get_dimension_string(var) == var
            if dimensionStringIsVarName:
                result.append(var)
        return result


    def get_ref_coordinate_variables(self):
        ref_coordinate_variables = []
        if not self.get_reference_variables():
            return ref_coordinate_variables
        ref_variable = self.get_reference_variables()[0]
        dimension_string = self.get_dimension_string(ref_variable)
        dimensions = dimension_string.split(' ')
        for var in self.data_set.variables:
            if self.get_dimension_string(var) in dimensions and self.is_coordinate_variable(self.data_set.variables[var]):
                ref_coordinate_variables.append(var)
        return ref_coordinate_variables


    def has_model_dimension(self, dimension_name):
        return dimension_name in self.data_set.dimensions


    def attribute(self, var_name, attribute_name):
        variable_attribute = self.get_variable_attribute(var_name, attribute_name)
        return variable_attribute
