class Exporter:

    def initialize(self, algorithmNames):
        raise NotImplementedError

    def finalize(self):
        raise NotImplementedError

    def addData(self, variableName, lat, lon, statistics):
        raise NotImplementedError

class Configuration:

    def setExport(self, exporter):
        self.exporter = exporter

    def setAlgorithms(self, algorithms):
        self.algorithms = algorithms

    def getExporter(self):
        return self.exporter

    def getAlgorithms(self):
        return self.algorithms