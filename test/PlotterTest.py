import unittest
#import matplotlib.pyplot as pypl
import numpy as np
from opec import Processor
import opec.Plotter as plotter
import os

class PlotterTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.cwd = os.getcwd()
        os.chdir('..')

    @classmethod
    def tearDownClass(self):
        os.chdir(self.cwd)

    def test_taylor_diagram(self):
        values = np.array([0, 15, 2, 3, 15, 8, 5, 3, 9, 11, 12, 1, 7, 7, 6])
        reference_values = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats = Processor.calculate_statistics(model_values=values, reference_values=reference_values)

        values1 = np.array([2, 14, 8, 6, 10, 9, 6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values1 = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats1 = Processor.calculate_statistics(model_values=values1, reference_values=reference_values1, model_name='Kate')

        values2 = np.array([-2, -14, -8, -6, -10, -9, -6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values2 = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats2 = Processor.calculate_statistics(model_values=values2, reference_values=reference_values2)

     #   print('ref_stddev: %s' % stats['ref_stddev'])
     #   print('stddev: %s' % stats['stddev'])
     #   print('unbiased rmse: %s' % stats['unbiased_rmse'])
     #   print('corrcoeff: %s' % stats['corrcoeff'])

     #   print('ref_stddev: %s' % stats2['ref_stddev'])
     #   print('stddev: %s' % stats2['stddev'])
     #   print('unbiased rmse: %s' % stats2['unbiased_rmse'])
     #   print('corrcoeff: %s' % stats2['corrcoeff'])

        diagram = plotter.create_taylor_diagram((stats, stats1), 10)
        diagram.plot_sample(stats2['corrcoeff'], stats2['stddev'], model_name='Linda')
        diagram.write('resources/taylor_test.png')
        # pypl.show()

    def test_target_diagram(self):
        values = np.array([0, 15, 2, 3, 15, 8, 5, 3, 9, 11, 12, 1, 7, 7, 6])
        reference_values = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats = Processor.calculate_statistics(model_values=values, reference_values=reference_values)

        values1 = np.array([2, 14, 8, 6, 10, 9, 6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values1 = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats1 = Processor.calculate_statistics(model_values=values1, reference_values=reference_values1, model_name='Kate')

        values2 = np.array([-2, -14, -8, -6, -10, -9, -6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values2 = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats2 = Processor.calculate_statistics(model_values=values2, reference_values=reference_values2)

     #   print('ref_stddev: %s' % stats['ref_stddev'])
     #   print('stddev: %s' % stats['stddev'])
     #   print('unbiased rmse: %s' % stats['unbiased_rmse'])
     #   print('corrcoeff: %s' % stats['corrcoeff'])

     #   print('ref_stddev: %s' % stats2['ref_stddev'])
     #   print('stddev: %s' % stats2['stddev'])
     #   print('unbiased rmse: %s' % stats2['unbiased_rmse'])
     #   print('corrcoeff: %s' % stats2['corrcoeff'])

        diagram = plotter.create_target_diagram((stats, stats1))
        diagram.write('resources/target_test.png')
        # pypl.show()

    def test_scatter_plot(self):
        values = np.array([0, -15, 2, 3, 15, 8, 5, 3, 9, 11, 12, 1, 7, 7, 6])
        reference_values = np.array([-9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])

        diagram = plotter.create_scatter_plot(reference_values, values, 'Modelled_toads', 'Toads', 'kg')

        diagram.write('resources/scatter_test.png')

        # pypl.show()