from util import Exporter

class CsvExporter(Exporter):

    def __init__(self, targetFilename):
        self.targetFile = open(targetFilename, "a")

    def addData(self, variableName, lat, lon, statistics):
        self.targetFile.write(variableName + "\t")
        self.targetFile.write(str(lat))
        self.targetFile.write("\t")
        self.targetFile.write(str(lon))
        self.targetFile.write("\t")
        count = 0
        max = len(statistics.keys())
        for stat in sorted(statistics):
            self.targetFile.write(str(statistics[stat]))
            count += 1
            if count < max:
                self.targetFile.write("\t")
        self.targetFile.write("\n")

    def initialize(self, algorithmNames):
        self.targetFile.write("variable_name\t")
        self.targetFile.write("lat\t")
        self.targetFile.write("lon\t")
        count = 0
        max = len(algorithmNames)
        for algorithmName in sorted(algorithmNames):
            self.targetFile.write(algorithmName)
            count += 1
            if count < max:
                self.targetFile.write("\t")
        self.targetFile.write("\n")

    def finalize(self):
        self.targetFile.close()