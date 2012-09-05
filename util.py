class Exporter:

    def initialize(self, algorithmNames):
        raise NotImplementedError

    def finalize(self):
        raise NotImplementedError

    def addData(self, variableName, lat, lon, statistics):
        raise NotImplementedError