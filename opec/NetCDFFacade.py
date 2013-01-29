import functools
from netCDF4 import Dataset

class NetCDFFacade(object):

    def __init__(self, filename):
        try:
            self.dataSet = Dataset(filename, 'r', format='NETCDF4_CLASSIC')
        except RuntimeError as re:
            raise ValueError('%s: %s' % (re.args[0], filename))

    def get_dim_size(self, dimName):
        dimensions = self.dataSet.dimensions
        for currentDimName in dimensions:
            if currentDimName == dimName:
                return len(dimensions[currentDimName])

    def get_global_attribute(self, attributeName):
        globalAttributes = self.dataSet.ncattrs
        for currentAttribute in globalAttributes():
            if currentAttribute == attributeName:
                return self.dataSet.__getattribute__(attributeName)

    def get_variable(self, variableName):
        variables = self.dataSet.variables
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
        self.dataSet.close()

    def get_dimensions(self, variable_name=None):
        result = []
        if variable_name is None:
            for dimension in self.dataSet.dimensions:
                result.append(dimension)
            return result
        variable = self.get_variable(variable_name)
        return variable._getdims()

    def is_coordinate_or_reference_variable(self, ncVariable):
        return len(ncVariable._getdims()) == 1

    def get_model_variables(self):
        result = []
        for variableName in self.dataSet.variables:
            ncVariable = self.get_variable(variableName)
            if not self.is_coordinate_or_reference_variable(ncVariable):
                result.append(variableName)
        return result

    def read_variable_fully(self, variableName):
        return self.get_variable(variableName)

    def get_variable_size(self, variableName):
        shape = self.dataSet.variables[variableName].shape
        return functools.reduce(lambda x, y: x * y, shape)

    def is_reference_variable(self, ncVariable):
        return self.is_coordinate_or_reference_variable(ncVariable) and self.has_coordinates_attribute(ncVariable)

    def is_coordinate_variable(self, ncVariable):
        return self.is_coordinate_or_reference_variable(ncVariable) and not self.has_coordinates_attribute(ncVariable)

    def get_reference_variables(self):
        result = []
        for variableName in self.dataSet.variables:
            ncVariable = self.get_variable(variableName)
            if self.is_reference_variable(ncVariable):
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
        for var in self.dataSet.variables:
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
        for var in self.dataSet.variables:
            if self.get_dimension_string(var) == dimension_string and self.is_coordinate_variable(self.dataSet.variables[var]):
                ref_coordinate_variables.append(var)
        return ref_coordinate_variables

    def has_model_dimension(self, dimension_name):
        return dimension_name in self.dataSet.dimensions