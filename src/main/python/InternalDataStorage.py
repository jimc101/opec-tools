import uuid
from tables import *
from src.main.python.NetcdfFacade import NetCDFFacade
import os
import numpy

class InternalDataStorage(object):

    def __init__(self, *args, **kwargs):
        if 'inputFile' in kwargs:
            netcdfFile = NetCDFFacade(kwargs['inputFile'])
        else:
            netcdfFile = NetCDFFacade(args[0].path)

        self.__create_storage_file()
        self.__create_coordinate_tables(netcdfFile)
        self.__create_model_tables(netcdfFile)
        self.__create_reference_tables(netcdfFile)
        self.__fill_tables(netcdfFile)

    def __del__(self):
        self.close()

    def close(self):
        if os.path.exists(self.filename):
            self.h5file.close()
            os.remove(self.filename)

    def __create_storage_file(self):
        self.filename = 'temp_' + str(uuid.uuid4()) + '.h5' # TODO - replace by temporary file read from configuration
        self.h5file = openFile(self.filename, mode="w", title="temporary data storage")

    def __create_coordinate_tables(self, netcdfFile):
        self.coordinateTables = {'lat': self.h5file.createTable("/", 'lat', Latitude),
                                 'lon': self.h5file.createTable("/", 'lon', Longitude),
                                 'time': self.h5file.createTable("/", 'time', Time)}
        if 'depth' in netcdfFile.get_coordinate_variables():
            self.coordinateTables['depth'] = self.h5file.createTable("/", 'depth', Depth)

    def __create_model_tables(self, netcdfFile):
        self.modelTables = {}
        for var in netcdfFile.get_model_variables():
            self.modelTables[var] = self.h5file.createTable("/", var, ModelVariable)

    def __fill_tables(self, netcdfFile):
        self.__fill_measurement_tables(netcdfFile, self.modelTables, 'modelVar')
        self.__fill_measurement_tables(netcdfFile, self.referenceTables, 'referenceVar')
        self.__fill_table(netcdfFile, self.coordinateTables['lat'], 'lat')
        self.__fill_table(netcdfFile, self.coordinateTables['lon'], 'lon')
        self.__fill_table(netcdfFile, self.coordinateTables['time'], 'time')
        if 'depth' in netcdfFile.get_coordinate_variables():
            self.__fill_table(netcdfFile, self.coordinateTables['depth'], 'depth')
        self.h5file.flush()

    def __fill_measurement_tables(self, netcdfFile, measurementTables, fieldName):
        for variableName in measurementTables:
            self.__fill_table(netcdfFile, measurementTables[variableName], fieldName, variableName)

    def __fill_table(self, netcdfFile, table, fieldName, variableName=None):
        if variableName is None:
            variableName = fieldName
        record = table.row
        variableData = netcdfFile.read_variable_fully(variableName)
        variableData = numpy.reshape(variableData, netcdfFile.get_variable_size(variableName))
        for value in variableData:
            record[fieldName] = value
            record.append()

    def __create_reference_tables(self, netcdfFile):
        self.referenceTables = {}
        for var in netcdfFile.get_reference_variables():
            self.referenceTables[var] = self.h5file.createTable("/", var, ReferenceVariable)

    def get_model_vars(self):
        return self.__get_vars(self.modelTables)

    def get_ref_vars(self):
        return self.__get_vars(self.referenceTables)

    def __get_vars(self, tables):
        vars = []
        for var in tables:
            vars.append(var)
        return vars

# todo - check if more datatypes are needed
class ModelVariable(IsDescription):
    modelVar = Float32Col()

class ReferenceVariable(IsDescription):
    referenceVar = Float32Col()

class Latitude(IsDescription):
    lat = Float32Col()

class Longitude(IsDescription):
    lon = Float32Col()

class Depth(IsDescription):
    depth = Float32Col()

class Time(IsDescription):
    time = Int32Col()