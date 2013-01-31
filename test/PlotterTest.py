import unittest
#import matplotlib.pyplot as pypl
import numpy as np
from opec import Processor
from opec.Configuration import Configuration
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
        stats = Processor.calculate_statistics(model_values=values, reference_values=reference_values, unit='mg')

        values1 = np.array([2, 14, 8, 6, 10, 9, 6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values1 = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats1 = Processor.calculate_statistics(model_values=values1, reference_values=reference_values1, model_name='Kate', unit='mg')

        values2 = np.array([-2, -14, -8, -6, -10, -9, -6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values2 = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats2 = Processor.calculate_statistics(model_values=values2, reference_values=reference_values2, unit='g')

     #   print('ref_stddev: %s' % stats['ref_stddev'])
     #   print('stddev: %s' % stats['stddev'])
     #   print('unbiased rmse: %s' % stats['unbiased_rmse'])
     #   print('corrcoeff: %s' % stats['corrcoeff'])

     #   print('ref_stddev: %s' % stats2['ref_stddev'])
     #   print('stddev: %s' % stats2['stddev'])
     #   print('unbiased rmse: %s' % stats2['unbiased_rmse'])
     #   print('corrcoeff: %s' % stats2['corrcoeff'])

        diagram = plotter.create_taylor_diagrams((stats, stats1))[0]
        diagram.plot_sample(stats2['corrcoeff'], stats2['stddev'], model_name='Linda', unit=stats2['unit'])
        diagram.write('resources/taylor_test.png')
        # pypl.show()

    def test_taylor_diagrams(self):
        values = np.array([0, 15, 2, 3, 15, 8, 5, 3, 9, 11, 12, 1, 7, 7, 6])
        reference_values = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats = Processor.calculate_statistics(model_values=values, reference_values=reference_values, model_name='Kate', unit='megazork')

        values1 = np.array([2, 14, 8, 6, 10, 9, 6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values1 = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats1 = Processor.calculate_statistics(model_values=values1, reference_values=reference_values1, model_name='Linda', unit='megazork')

        values2 = np.array([-2, -14, -8, -6, -10, -9, -6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values2 = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats2 = Processor.calculate_statistics(model_values=values2, reference_values=reference_values2, model_name='Linda', unit='gimpel/m^3')

        diagrams = plotter.create_taylor_diagrams((stats, stats1, stats2))
        self.assertEqual(2, len(diagrams))

        for i, d in enumerate(diagrams):
            d.write('resources/taylor_test_%s.png' % i)

        # pypl.show()

    def test_target_diagram(self):
        values =           np.array([0, 15, 2, 3, 15, 8, 5, 3, 9, 11, 12, 1, 7, 7, 6])
        reference_values = np.array([2, 14, 1, 4, 12, 3, 7, 5, 7, 12, 13, 3, 5, 6, 8])
        stats = Processor.calculate_statistics(model_values=values, reference_values=reference_values)

        values1 =           np.array([2, 14, 8, 6, 10, 9, 6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values1 = np.array([5, 11, 6, 4, 11, 8, 7, 9, 2, 5, 11, -2, 1, 3, 9])
        stats1 = Processor.calculate_statistics(model_values=values1, reference_values=reference_values1, model_name='Kate')

        values2 =           np.array([-2, -14, -8, -6, -10, -9, -6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values2 = np.array([-1, -10, -5, -5, -11, -8, -7, 5, 3, 13, 10, 2, 2, -1, 7])
        stats2 = Processor.calculate_statistics(model_values=values2, reference_values=reference_values2)

     #   print('ref_stddev: %s' % stats['ref_stddev'])
     #   print('stddev: %s' % stats['stddev'])
     #   print('unbiased rmse: %s' % stats['unbiased_rmse'])
     #   print('corrcoeff: %s' % stats['corrcoeff'])

     #   print('ref_stddev: %s' % stats2['ref_stddev'])
     #   print('stddev: %s' % stats2['stddev'])
     #   print('unbiased rmse: %s' % stats2['unbiased_rmse'])
     #   print('corrcoeff: %s' % stats2['corrcoeff'])

        config = Configuration(target_diagram_bounds=[-0.8, None, -0.8, 0.3])
        diagram = plotter.create_target_diagram((stats, stats1, stats2), config)
        diagram.write('resources/target_test.png')
        # pypl.show()

    def test_scatter_plot(self):
        values = np.array([0, -15, 2, 3, 15, 8, 5, 3, 9, 11, 12, 1, 7, 7, 6])
        reference_values = np.array([-9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])

        diagram = plotter.create_scatter_plot(reference_values, values, 'Modelled_toads', 'Toads', 'kg')

        diagram.write('resources/scatter_test.png')

        # pypl.show()