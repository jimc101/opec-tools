from src.main.python.NetCDFFacade import NetCDFFacade

class Data(object):

    def __init__(self, inputFile):
        self.netcdf = NetCDFFacade(inputFile)

    def model_vars(self):
        return self.netcdf.get_model_variables()

    def close(self):
        self.netcdf.close()

    def ref_vars(self):
        return self.netcdf.get_reference_variables()

