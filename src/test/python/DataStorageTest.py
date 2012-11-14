import unittest
import numpy
from src.main.python.Configuration import *
from src.main.python.DataStorage import DataStorage

class DataStorageTest(unittest.TestCase):

    def testInitialisation(self):
        dictionary = {PROPERTY_INPUT_FILE: "../resources/test.nc"}
        config = Configuration(dictionary)
        self.dataStorage = DataStorage(config)
        self.assertIsNotNone(self.dataStorage.latitude)
        self.assertIsNotNone(self.dataStorage.longitude)
        self.assertIsNotNone(self.dataStorage.depth)
        self.assertIsNotNone(self.dataStorage.time)

        latitudes = self.dataStorage.latitude.read()
        self.assertEqual(numpy.ndarray, type(latitudes))
        self.assertEqual((2,), latitudes.shape)
        self.assertAlmostEqual(55.2, latitudes[0][0], 4)
        self.assertAlmostEqual(56.8, latitudes[1][0], 4)

        longitudes = self.dataStorage.longitude.read()
        self.assertEqual(numpy.ndarray, type(longitudes))
        self.assertEqual((4,), longitudes.shape)
        self.assertAlmostEqual(5.3, longitudes[0][0], 4)
        self.assertAlmostEqual(5.8, longitudes[1][0], 4)
        self.assertAlmostEqual(6.3, longitudes[2][0], 4)
        self.assertAlmostEqual(6.8, longitudes[3][0], 4)

        depths = self.dataStorage.depth.read()
        self.assertEqual(numpy.ndarray, type(depths))
        self.assertEqual((2,), depths.shape)
        self.assertAlmostEqual(0.001, depths[0][0], 4)
        self.assertAlmostEqual(0.002, depths[1][0], 4)

        times = self.dataStorage.time.read()
        self.assertEqual(numpy.ndarray, type(times))
        self.assertEqual((2,), times.shape)
        self.assertAlmostEqual(1261440000, times[0][0], 4)
        self.assertAlmostEqual(1261447200, times[1][0], 4)

    def tearDown(self):
        self.dataStorage.close()
