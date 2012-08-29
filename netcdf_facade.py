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

    def getData(self, variableName, origin, shape):
        variable = self.getVariable(variableName)
        return variable[1, 2]
#        return variable[origin[0], origin[1], shape[0]]

    def close(self):
        self.dataSet.close()