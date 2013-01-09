import unittest
#import matplotlib.pyplot as pypl
import numpy as np
from src.main.python import Processor
import src.main.python.Plotter as plotter

class PlotterTest(unittest.TestCase):

    def test_taylor_diagram(self):
        values = np.array([0, 15, 2, 3, 15, 8, 5, 3, 9, 11, 12, 1, 7, 7, 6])
        reference_values = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats = Processor.calculate_statistics(model_values=values, reference_values=reference_values)

        values1 = np.array([2, 14, 8, 6, 10, 9, 6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values1 = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats1 = Processor.calculate_statistics(model_values=values1, reference_values=reference_values1)

        print('ref_stddev: %s' % stats['ref_stddev'])
        print('stddev: %s' % stats['stddev'])
        print('centered rsmd: %s' % stats['centered_rmsd'])
        print('corrcoeff: %s' % stats['corrcoeff'])

        print('ref_stddev: %s' % stats1['ref_stddev'])
        print('stddev: %s' % stats1['stddev'])
        print('centered rsmd: %s' % stats1['centered_rmsd'])
        print('corrcoeff: %s' % stats1['corrcoeff'])

        plotter.create_taylor_diagram(stats['ref_stddev'], (stats, stats1), '../resources/taylor_test.png')
        # pypl.show()