import os
import unittest
import numpy
from src.main.python.DataStorage import DataStorage
from src.main.python.Main import parseArguments

class DataStorageTest(unittest.TestCase):

    def testInitialisationWithString(self):
        self.dataStorage = DataStorage(inputFile = "../resources/test.nc")

    def testInitialisation(self):
        args = parseArguments(["../resources/test.nc"])
        self.dataStorage = DataStorage(args)
        self.assertCreationOfCoordinateTables()
        self.assertCoordinateTablesFilled()
        self.assertGeophysicalTablesCreated()
        self.assertGeophysicalTablesFilled()

    def assertCreationOfCoordinateTables(self):
        self.assertIsNotNone(self.dataStorage.latitude)
        self.assertIsNotNone(self.dataStorage.longitude)
        self.assertIsNotNone(self.dataStorage.depth)
        self.assertIsNotNone(self.dataStorage.time)

    def assertCoordinateTablesFilled(self):
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
        self.assertFalse(os.path.exists(self.dataStorage.filename))

    def assertGeophysicalTablesCreated(self):
        pass

    def assertGeophysicalTablesFilled(self):
        pass
