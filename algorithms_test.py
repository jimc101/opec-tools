import unittest
from numpy import array
from algorithms import rootMeanSquareDeviation

class AlgorithmTest(unittest.TestCase):

    def testRootMeanSquareDeviation(self):
        values = array(range(5, 20, 2)) # [5, 7, 9, 11, 13, 15, 17, 19]
        self.assertAlmostEqual(7.54983, rootMeanSquareDeviation(values, 6), 5)
