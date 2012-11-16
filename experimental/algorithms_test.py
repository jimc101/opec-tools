import unittest
from numpy import array
import numpy
from experimental.algorithms import computeRmsd, computeBias, computeUnbiasedRmsd, computeCorrelation
from src.main.python.NetcdfFacade import NetCDFFacade

class AlgorithmTest(unittest.TestCase):

    def testRootMeanSquareDeviation(self):
        values = array(range(5, 20, 2)) # [5, 7, 9, 11, 13, 15, 17, 19]
        referenceValues = array([6, 6, 6, 6, 6, 6, 6, 6])
        self.assertAlmostEqual(7.54983, computeRmsd(values, referenceValues), 5)

    def testRootMeanSquareDeviation_WrongUsage(self):
        values = array([1, 2, 3]) # [5, 7, 9, 11, 13, 15, 17, 19]
        referenceValues = array([1, 2])
        try:
            computeRmsd(values, referenceValues)
            self.fail()
        except ValueError:
            pass # ok

    def testRMSDOnActualValues(self):
        netcdf = NetCDFFacade('resources\\test.nc')
        data = netcdf.getData('chl', [1, 0, 0], [1, 2, 4])
        data = data.reshape(-1)
        referenceData = array([14, 14, 14, 14, 14, 14, 14, 14])
        self.assertAlmostEqual(2.345208, computeRmsd(data, referenceData), 5)

    def testBias(self):
        values = array(range(5, 20, 2)) # [5, 7, 9, 11, 13, 15, 17, 19]
        referenceValues = numpy.arange(5, 20, 2.1) # [5, 7.1, 9.2, 11.3, 13.4, 15.5, 17.6, 19.7]; mean = 12.35
        self.assertAlmostEqual(0.35, computeBias(values, referenceValues), 5)

    def testUnbiasedRmsd(self):
        values = array(range(1, 5, 1)) # [1, 2, 3, 4]
        referenceData = array([1.1, 2.2, 2.9, 3.7])
        self.assertAlmostEqual(0.192028, computeUnbiasedRmsd(values, referenceData), 5)

    def testCorrespondenceBetweenRmsdBiasAndUnbiasedRmsd(self):
        values = array(range(1, 5, 1)) # [1, 2, 3, 4]
        referenceData = array([1.8, 1.9, 3.01, 4.0])
        rms = computeRmsd(values, referenceData)
        bias = computeBias(values, referenceData)
        unbiasedRmsd = computeUnbiasedRmsd(values, referenceData)
        self.assertAlmostEqual(rms ** 2, bias ** 2 + unbiasedRmsd ** 2, 5)

    def testCorrelation(self):
        values = array(range(1, 5, 1)) # [1, 2, 3, 4]
        referenceData = array([1.8, 1.9, 3.01, 4.0])
        self.assertAlmostEqual(0.958659, computeCorrelation(values, referenceData), 5)