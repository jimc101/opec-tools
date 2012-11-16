from src.main.python import NetcdfFacade

__author__ = 'Thomas Storm'

class MatchupCreator:

    def __init__(self, filename):
        self.netcdf = NetcdfFacade.NetCDFFacade(filename)
        self.coordinateVariables = []
        dimensions = self.netcdf.get_dimensions()
        for dimension in dimensions:
            if self.netcdf.get_variable(dimension) is not None:
                origin = [0]
                shape = [self.netcdf.get_dim_size(dimension)]
                values = self.netcdf.get_data(dimension, origin, shape)
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