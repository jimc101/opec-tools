from netCDF4 import Dataset

class NetCDFFacade(object):

    def __init__(self, filename):
        self.dataSet = Dataset(filename, 'r', format='NETCDF4_CLASSIC')

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
        return variable.__getattribute__(attributeName)

    def get_dimension_string(self, variableName):
        variable = self.get_variable(variableName)
        dimensionString = ""
        for dimName in variable._getdims():
            dimensionString = dimensionString + dimName + " "
        dimensionString = dimensionString.strip()
        return dimensionString

    def get_dim_length(self, variableName, index):
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
        indexArray = range(0, dimCount)
        for dimIdx in range(dimCount):
            j = 0
            innerArray = range(0, shape[dimIdx])
            for index in range(origin[dimIdx], origin[dimIdx] + shape[dimIdx]):
                innerArray[j] = index
                j += 1
            indexArray[dimIdx] = innerArray
        return variable[indexArray]

    def close(self):
        self.dataSet.close()

    def get_dimensions(self):
        result = []
        for dimension in self.dataSet.dimensions:
            result.append(dimension)
        return result

    def get_geophysical_variables(self):
        result = []
        for variableName in self.dataSet.variables:
            ncVariable = self.get_variable(variableName)
            isCoordinateVariable = len(ncVariable._getdims()) == 1
            if not isCoordinateVariable:
                result.append(variableName)
        return result

    def read_variable_fully(self, variableName):
        return self.get_variable(variableName)

    def get_variable_size(self, variableName):
        shape = self.dataSet.variables[variableName].shape
        return reduce(lambda x, y: x * y, shape)

