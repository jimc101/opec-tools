from netCDF4 import Dataset

class NetCDFFacade:

    def __init__(self, filename):
        self.dataSet = Dataset(filename, 'r', format='NETCDF4_CLASSIC')

    def getDimSize(self, dimName):
        dimensions = self.dataSet.dimensions
        for currentDimName in dimensions:
            if currentDimName == dimName:
                return len(dimensions[currentDimName])

    def getGlobalAttribute(self, attributeName):
        globalAttributes = self.dataSet.ncattrs
        for currentAttribute in globalAttributes():
            if currentAttribute == attributeName:
                return self.dataSet.__getattribute__(attributeName)

    def getVariable(self, variableName):
        variables = self.dataSet.variables
        for currentVarName in variables:
            if currentVarName == variableName:
                return variables[currentVarName]
        return None

    def getVariableAttribute(self, variableName, attributeName):
        variable = self.getVariable(variableName)
        return variable.__getattribute__(attributeName)

    def getDimensionString(self, variableName):
        variable = self.getVariable(variableName)
        dimensionString = ""
        for dimName in variable._getdims():
            dimensionString = dimensionString + dimName + " "
        dimensionString = dimensionString.strip()
        return dimensionString

    def getDimLength(self, variableName, index):
        variable = self.getVariable(variableName)
        variableDimensions = variable._getdims()
        for i in range(len(variableDimensions)):
            if i == index:
                dimName = variableDimensions[i]
                return self.getDimSize(dimName)

    def getData(self, variableName, origin, shape):
        variable = self.getVariable(variableName)
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

    def getDimensions(self):
        result = []
        for dimension in self.dataSet.dimensions:
            result.append(dimension)
        return result

    def getGeophysicalVariables(self):
        result = []
        for variableName in self.dataSet.variables:
            ncVariable = self.getVariable(variableName)
            isCoordinateVariable = len(ncVariable._getdims()) == 1
            if not isCoordinateVariable:
                result.append(variableName)
        return result

    def readVariableFully(self, variableName):
        return self.getVariable(variableName)

    def getVariableSize(self, variableName):
        shape = self.dataSet.variables[variableName].shape
        return reduce(lambda x, y: x * y, shape)

