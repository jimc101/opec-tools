# Copyright (C) 2013 Brockmann Consult GmbH (info@brockmann-consult.de)
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see http://www.gnu.org/licenses/gpl.html

import unittest
#import matplotlib.pyplot as pypl
import numpy as np
from opec import processor
import opec.plotter as plotter
import os

class Plotter_test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.cwd = os.getcwd()
        os.chdir('..')

    @classmethod
    def tearDownClass(self):
        os.chdir(self.cwd)

    @unittest.skip('shall not run in production environment')
    def test_taylor_diagram(self):
        values = np.array([0, 15, 2, 3, 15, 8, 5, 3, 9, 11, 12, 1, 7, 7, 6])
        reference_values = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats = processor.calculate_statistics(model_values=values, reference_values=reference_values, unit='mg')

        values1 = np.array([2, 14, 8, 6, 10, 9, 6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values1 = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats1 = processor.calculate_statistics(model_values=values1, reference_values=reference_values1, model_name='Kate', unit='mg')

        values2 = np.array([-2, -14, -8, -6, -10, -9, -6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values2 = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats2 = processor.calculate_statistics(model_values=values2, reference_values=reference_values2, unit='g')

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

    @unittest.skip('shall not run in production environment')
    def test_taylor_diagrams(self):
        values = np.array([0, 15, 2, 3, 15, 8, 5, 3, 9, 11, 12, 1, 7, 7, 6])
        reference_values = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats = processor.calculate_statistics(model_values=values, reference_values=reference_values, model_name='Kate', unit='megazork')

        values1 = np.array([2, 14, 8, 6, 10, 9, 6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values1 = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats1 = processor.calculate_statistics(model_values=values1, reference_values=reference_values1, model_name='Linda', unit='megazork')

        values2 = np.array([-2, -14, -8, -6, -10, -9, -6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values2 = np.array([9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])
        stats2 = processor.calculate_statistics(model_values=values2, reference_values=reference_values2, model_name='Linda', unit='gimpel/m^3')

        diagrams = plotter.create_taylor_diagrams((stats, stats1, stats2))
        self.assertEqual(2, len(diagrams))

        for i, d in enumerate(diagrams):
            d.write('resources/taylor_test_%s.png' % i)

        # pypl.show()

    @unittest.skip('shall not run in production environment')
    def test_target_diagram(self):
        values =           np.array([3, 3, 2, 3, 6, 8, 5, 3, 4, 6, 4, 1, 7, 7, 6])
        reference_values = np.array([2, 5, 1, 5, 5, 9, 4, 5, 3, 8, 3, 3, 6, 9, 5])
        stats = processor.calculate_statistics(model_values=values, reference_values=reference_values, model_name='Linda', unit='g')

        values1 =           np.array([2, 14, 8, 6, 10, 9, 6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values1 = np.array([5, 11, 6, 4, 11, 8, 7, 9, 2, 5, 11, -2, 1, 3, 9])
        stats1 = processor.calculate_statistics(model_values=values1, reference_values=reference_values1, model_name='Kate', unit='mg')

        values2 =           np.array([-2, -14, -8, -6, -10, -9, -6, 7, 2, 15, 10, 0, 2, 2, 8])
        reference_values2 = np.array([-1, -10, -5, -5, -11, -8, -7, 5, 3, 13, 10, 2, 2, -1, 7])
        stats2 = processor.calculate_statistics(model_values=values2, reference_values=reference_values2, model_name='Naomi', unit='kg')

     #   print('ref_stddev: %s' % stats['ref_stddev'])
     #   print('stddev: %s' % stats['stddev'])
     #   print('unbiased rmse: %s' % stats['unbiased_rmse'])
     #   print('corrcoeff: %s' % stats['corrcoeff'])

     #   print('ref_stddev: %s' % stats2['ref_stddev'])
     #   print('stddev: %s' % stats2['stddev'])
     #   print('unbiased rmse: %s' % stats2['unbiased_rmse'])
     #   print('corrcoeff: %s' % stats2['corrcoeff'])

        diagram = plotter.create_target_diagram((stats, stats1, stats2))
        diagram.write('resources/target_test.png')
        # pypl.show()

    @unittest.skip('shall not run in production environment')
    def test_density_plot(self):
        values = np.array([0, -15, 2, 3, 15, 8, 5, 3, 9, 11, 12, 1, 7, 7, 6])
        reference_values = np.array([-9, 10, 1, 2, 11, 3, 7, 5, 4, 12, 7, 8, 5, 1, 14])

        diagram = plotter.create_density_plot(reference_values, values, 'Modelled_toads', 'Toads', 'kg')

        diagram.write('resources/density_test.png')

        # pypl.show()
