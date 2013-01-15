import numpy as np
from opec.NetCDFFacade import NetCDFFacade

class Data(dict):

    def __init__(self, input_file_name):
        super().__init__()
        self.__netcdf = NetCDFFacade(input_file_name)
        self.__current_storage = {}

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

    #todo - allow access to values that have been read, but not exactly the same shape as requested
    def read(self, variable_name, origin=None, shape=None):
        if self.__is_cached(variable_name):
            if self.__can_return_all(origin, shape, variable_name):
                return self[variable_name]
            if origin is not None and shape is not None:
                if self.__current_storage[variable_name] != 'fully_read':
                    current_slice = self.__current_storage[variable_name]
                    # if origin and shape exactly match origin and shape of what has been read before, return that
                    if np.array_equal(origin, current_slice[0]) and np.array_equal(shape, current_slice[1]):
                        return self[variable_name]
        must_fully_read = origin is None and shape is None
        if must_fully_read:
            self[variable_name] = self.__netcdf.get_variable(variable_name)[:]
            self.__current_storage[variable_name] = 'fully_read'
        else:
            self[variable_name] = self.__netcdf.get_data(variable_name, origin, shape)
            self.__current_storage[variable_name] = [np.array(origin), np.array(shape)]
        return self[variable_name]

    def __is_cached(self, variable_name):
        return variable_name in self.__current_storage.keys()

    def __can_return_all(self, origin, shape, variable_name):
        return origin is None and shape is None and self.__current_storage[variable_name] == 'fully_read'
