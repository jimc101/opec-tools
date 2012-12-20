from src.main.python.NetCDFFacade import NetCDFFacade

class Data(object):

    def __init__(self, inputFile):
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

