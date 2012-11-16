import uuid
from tables import *
from src.main.python.NetcdfFacade import NetCDFFacade
import os
import numpy

class DataStorage:

    def __init__(self, *args, **kwargs):
        if 'inputFile' in kwargs:
            netcdfFile = NetCDFFacade(kwargs['inputFile'])
        else:
            netcdfFile = NetCDFFacade(args[0].path)

        self.createStorageFile()
        self.createCoordinateTables()
        self.fillCoordinateTables(netcdfFile)
        self.createGeophysicalTables(netcdfFile)
        self.fillGeophysicalTables(netcdfFile)

    def close(self):
        self.h5file.close()
        os.remove(self.filename)

    def createStorageFile(self):
        self.filename = 'temp_' + str(uuid.uuid4()) + '.h5' # TODO - replace by temporary file read from configuration
        self.h5file = openFile(self.filename, mode="w", title="temporary data storage")

    def createCoordinateTables(self):
        self.latitude = self.h5file.createTable("/", 'lat', Latitude)
        self.longitude = self.h5file.createTable("/", 'lon', Longitude)
        self.depth = self.h5file.createTable("/", 'depth', Depth)
        self.time = self.h5file.createTable("/", 'time', Time)

    def fillCoordinateTables(self, netcdfFile):
        latDimLength = netcdfFile.getDimLength("lat", 0)
        lonDimLength = netcdfFile.getDimLength("lon", 0)
        depthDimLength = netcdfFile.getDimLength("depth", 0)
        timeDimLength = netcdfFile.getDimLength("time", 0)
        record = self.latitude.row
        for i in xrange(latDimLength):
            record['lat'] = netcdfFile.getData("lat", [i], [1]) # todo - optimise: this is maximally non-performant
            record.append()
        record = self.longitude.row
        for i in xrange(lonDimLength):
            record['lon'] = netcdfFile.getData("lon", [i], [1])
            record.append()
        self.h5file.flush()
        record = self.depth.row
        for i in xrange(depthDimLength):
            record['depth'] = netcdfFile.getData("depth", [i], [1])
            record.append()
        self.h5file.flush()
        record = self.time.row
        for i in xrange(timeDimLength):
            record['time'] = netcdfFile.getData("time", [i], [1])
            record.append()
        self.h5file.flush()

    def createGeophysicalTables(self, netcdfFile):
        self.geophysicalTables = {}
        for var in netcdfFile.getGeophysicalVariables():
            self.geophysicalTables[var] = self.h5file.createTable("/", var, GeophysicalVariable)

    def fillGeophysicalTables(self, netcdfFile):
        for var in self.geophysicalTables:
            variableData = netcdfFile.readVariableFully(var)
            variableData = numpy.reshape(variableData, netcdfFile.getVariableSize(var))
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