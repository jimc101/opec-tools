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
import functools

import logging
import unittest
import numpy as np
from numpy.testing import assert_array_equal
from opec.Data import Data
import os

class Data_test(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.test_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/test.nc"
        self.data = Data(self.test_file)

    def tearDown(self):
        logging.basicConfig(level=logging.WARNING)

    def test_model_vars(self):
        model_vars = self.data.model_vars()
        assert_array_equal(np.array(['chl', 'sst']), model_vars)

    def test_ref_vars(self):
        ref_vars = self.data.ref_vars()
        assert_array_equal(np.array(['chl_ref']), ref_vars)

    def test_reference_records_count(self):
        self.assertEqual(3, self.data.reference_records_count({'record_num'}))

    def test_gridded_reference_records_count(self):
        test_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/ogs_test.nc"
        self.data = Data(test_file)
        self.assertEqual(128 * 336, self.data.reference_records_count({'latitude', 'longitude'}))

    def test_find_model_latitude_variable_name(self):
        self.assertEqual('lat', self.data.find_model_latitude_variable_name())
        test_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/ogs_test.nc"
        self.data = Data(test_file)
        self.assertEqual('latitude', self.data.find_model_latitude_variable_name())

    def test_find_model_longitude_variable_name(self):
        self.assertEqual('lon', self.data.find_model_longitude_variable_name())
        test_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/ogs_test.nc"
        self.data = Data(test_file)
        self.assertEqual('longitude', self.data.find_model_longitude_variable_name())

    def tearDown(self):
        self.data.close()

    def test_var_access(self):
        chl_data = self.data.read_model('chl', [0, 0, 0, 0], [1, 1, 1, 1])
        self.assertEqual(np.ndarray, type(chl_data))
        self.assertAlmostEqual(0.1111, chl_data[0])

        self.data.read_model('chl')
        chl_data = self.data['chl']
        self.assertEqual(np.ndarray, type(chl_data))
        self.assertEqual(32, chl_data.size)

    def test_data_is_read_only_once_full_variable(self):
        self.data.read_model('chl')
        chl_data = self.data['chl']
        self.assertEqual(32, chl_data.size)
        self.assertAlmostEqual(0.1111, chl_data[0][0][0][0])

        self.data['chl'][0][0][0][0] = 0.5
        chl_data = self.data.read_model('chl')
        self.assertAlmostEqual(0.5, chl_data[0][0][0][0])

    def test_data_is_read_only_once_part_of_variable(self):
        origin = np.array([0, 0, 0, 1])
        shape = np.array([1, 1, 2, 2])
        num_read_values = functools.reduce(lambda x, y: x * y, shape)
        chl_data = self.data.read_model('chl', origin, shape)
        self.assertEqual(num_read_values, chl_data.size)
        self.assertAlmostEqual(0.2111, chl_data[0])
        self.assertAlmostEqual(0.1211, chl_data[1])
        self.assertAlmostEqual(0.2121, chl_data[2])
        self.assertAlmostEqual(0.1221, chl_data[3])

        self.data['chl'][0] = 0.5
        chl_data = self.data.read_model('chl', [0, 0, 0, 1], [1, 1, 2, 2])
        self.assertAlmostEqual(0.5, chl_data[0])

    def test_data_works_with_split_files(self):
        test_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/test_without_records.nc"
        test_ref_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/test_only_reference.nc"
        data = Data(test_file, test_ref_file)
        self.assertEqual(2, len(data.model_vars()))
        self.assertTrue('chl' in data.model_vars())
        self.assertTrue('sst' in data.model_vars())
        self.assertEqual(1, len(data.ref_vars()))
        self.assertTrue('chl_ref' in data.ref_vars())
        self.assertEqual(4, len(data.reference_coordinate_variables()))

    def test_unit(self):
        self.assertEqual('milligram m-3', self.data.unit('chl'))
        self.assertEqual('kelvin', self.data.unit('sst'))
        self.assertEqual('degrees_east', self.data.unit('lon_ref'))
        self.assertIsNone(self.data.unit('var_without_unit'))
        self.assertRaises(ValueError, lambda: self.data.unit('toad_count'))

    def test_gridded_reference_data(self):
        test_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/ogs_test.nc"
        data = Data(test_file)
        self.assertEqual(1, len(data.ref_vars()))
        self.assertEqual('Ref_chl', data.ref_vars()[0])