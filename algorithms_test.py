import unittest
from numpy import array
from algorithms import computeRmsd, computeBias, computeUnbiasedRmsd
from netcdf_facade import NetCDFFacade

class AlgorithmTest(unittest.TestCase):

    def testRootMeanSquareDeviation(self):
        values = array(range(5, 20, 2)) # [5, 7, 9, 11, 13, 15, 17, 19]
        self.assertAlmostEqual(7.54983, computeRmsd(values, 6), 5)

    def testRMSDOnActualValues(self):
        netcdf = NetCDFFacade('resources\\test.nc')
        data = netcdf.getData('chlorophyll_concentration_in_sea_water', [1, 0, 0], [1, 2, 4])
        data = data.reshape(-1)
        self.assertAlmostEqual(2.345208, computeRmsd(data, 14), 5)

    def testBias(self):
        values = array(range(5, 20, 2)) # [5, 7, 9, 11, 13, 15, 17, 19]
        self.assertAlmostEqual(2.0, computeBias(values, 14), 5)

    def testUnbiasedRmsd(self):
        values = array(range(5, 20, 2)) # [5, 7, 9, 11, 13, 15, 17, 19]
        self.assertAlmostEqual(4.582575, computeUnbiasedRmsd(values), 5)

    def testUnbiasedRmsd_2(self):
        values = array(range(1, 5, 1)) # [1, 2, 3, 4]
        self.assertAlmostEqual(1.1180339887498948482, computeUnbiasedRmsd(values), 5)

    def testCorrespondenceBetweenRmsdBiasAndUnbiasedRmsd(self):
        values = array(range(1, 5, 1)) # [1, 2, 3, 4]
        rms = computeRmsd(values, 3)
        bias = computeBias(values, 3)
        unbiasedRmsd = computeUnbiasedRmsd(values)
        self.assertAlmostEqual(rms ** 2, bias ** 2 + unbiasedRmsd ** 2, 5)