from src.main.python import NetcdfFacade

__author__ = 'Thomas Storm'

class MatchupCreator:

    def __init__(self, filename):
        self.netcdf = NetcdfFacade.NetCDFFacade(filename)
        self.coordinateVariables = []
        dimensions = self.netcdf.getDimensions()
        for dimension in dimensions:
            if self.netcdf.getVariable(dimension) is not None:
                origin = [0]
                shape = [self.netcdf.getDimSize(dimension)]
                values = self.netcdf.getData(dimension, origin, shape)
                coordinateVariable = CoordinateVariable(dimension, values)
                self.coordinateVariables.append(coordinateVariable)


    def close(self):
        self.netcdf.close()

    def getMatchups(self):
        pass

class CoordinateVariable:

    def __init__(self, name, values):
        self.name = name
        self.values = values