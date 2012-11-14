import unittest
from src.main.python.Configuration import Configuration, PROPERTY_INPUT_FILE

class ConfigurationTest(unittest.TestCase):

    def testInitialise(self):
        dictionary = {PROPERTY_INPUT_FILE : "path_to_input_file.nc"}
        config = Configuration(dictionary)
        self.assertEqual("path_to_input_file.nc", config.inputFile)
