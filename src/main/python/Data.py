from src.main.python.NetCDFFacade import NetCDFFacade
import numpy as np

class Data(dict):

    def __init__(self, inputFile):
        super().__init__()
        self.__netcdf = NetCDFFacade(inputFile)

    def model_vars(self):
        return self.__netcdf.get_model_variables()

    def close(self):
        self.__netcdf.close()

    def ref_vars(self):
        return self.__netcdf.get_reference_variables()

    def has_variable(self, variable_name):
        return self.__netcdf.has_variable(variable_name)

    def reference_coordinate_variables(self):
        return self.__netcdf.get_ref_coordinate_variables()

    def dim_size(self, dim_name):
        return self.__netcdf.get_dim_size(dim_name)

    def dimension_string(self, variable_name):
        return self.__netcdf.get_dimension_string(variable_name)

    def reference_records_count(self):
        ref_vars = self.ref_vars()
        if not ref_vars:
            return 0
        return self.dim_size(self.dimension_string(ref_vars[0]))

    def read(self, variable_name, origin=None, shape=None):
        if origin is None and shape is None:
            self[variable_name] = self.__netcdf.get_variable(variable_name)[:]
        else:
            self[variable_name] = self.__netcdf.get_data(variable_name, origin, shape)

    def clear(self, variable_name=None):
        if variable_name is None:
            super(Data, self).clear()
        self[variable_name] = np.array([])