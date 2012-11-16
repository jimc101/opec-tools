import uuid
from tables import *
from src.main.python.NetcdfFacade import NetCDFFacade
import os
import numpy

class DataStorage(object):

    def __init__(self, *args, **kwargs):
        if 'inputFile' in kwargs:
            netcdfFile = NetCDFFacade(kwargs['inputFile'])
        else:
            netcdfFile = NetCDFFacade(args[0].path)

        self.__create_storage_file()
        self.__create_coordinate_tables()
        self.__fill_coordinate_tables(netcdfFile)
        self.__create_geophysical_tables(netcdfFile)
        self.__fill_geophysical_tables(netcdfFile)

    def close(self):
        self.h5file.close()
        os.remove(self.filename)

    def __create_storage_file(self):
        self.filename = 'temp_' + str(uuid.uuid4()) + '.h5' # TODO - replace by temporary file read from configuration
        self.h5file = openFile(self.filename, mode="w", title="temporary data storage")

    def __create_coordinate_tables(self):
        self.latitude = self.h5file.createTable("/", 'lat', Latitude)
        self.longitude = self.h5file.createTable("/", 'lon', Longitude)
        self.depth = self.h5file.createTable("/", 'depth', Depth)
        self.time = self.h5file.createTable("/", 'time', Time)

    def __fill_coordinate_tables(self, netcdfFile):
        latDimLength = netcdfFile.get_dim_length("lat", 0)
        lonDimLength = netcdfFile.get_dim_length("lon", 0)
        depthDimLength = netcdfFile.get_dim_length("depth", 0)
        timeDimLength = netcdfFile.get_dim_length("time", 0)
        record = self.latitude.row
        for i in xrange(latDimLength):
            record['lat'] = netcdfFile.get_data("lat", [i], [1]) # todo - optimise: this is maximally non-performant
            record.append()
        record = self.longitude.row
        for i in xrange(lonDimLength):
            record['lon'] = netcdfFile.get_data("lon", [i], [1])
            record.append()
        self.h5file.flush()
        record = self.depth.row
        for i in xrange(depthDimLength):
            record['depth'] = netcdfFile.get_data("depth", [i], [1])
            record.append()
        self.h5file.flush()
        record = self.time.row
        for i in xrange(timeDimLength):
            record['time'] = netcdfFile.get_data("time", [i], [1])
            record.append()
        self.h5file.flush()

    def __create_geophysical_tables(self, netcdfFile):
        self.geophysicalTables = {}
        for var in netcdfFile.get_geophysical_variables():
            self.geophysicalTables[var] = self.h5file.createTable("/", var, GeophysicalVariable)

    def __fill_geophysical_tables(self, netcdfFile):
        for var in self.geophysicalTables:
            variableData = netcdfFile.read_variable_fully(var)
            variableData = numpy.reshape(variableData, netcdfFile.get_variable_size(var))
            record = self.geophysicalTables[var].row
            for value in variableData:
                record['geophysicalVar'] = value
                record.append()
        self.h5file.flush()


# todo - check if more datatypes are needed
class GeophysicalVariable(IsDescription):
    geophysicalVar = Float32Col()

class Latitude(IsDescription):
    lat = Float32Col()

class Longitude(IsDescription):
    lon = Float32Col()

class Depth(IsDescription):
    depth = Float32Col()

class Time(IsDescription):
    time = Int32Col()