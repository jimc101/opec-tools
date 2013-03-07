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

import logging
import unittest
import os

import numpy as np
from numpy.testing import assert_array_equal

from opec.Data import Data


class Data_test(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.test_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/test.nc"
        self.data = Data(self.test_file)

    def tearDown(self):
        self.data.close()
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
        test_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/ogs_test_smaller.nc"
        data = Data(test_file)
        self.assertEqual(41 * 80, data.reference_records_count({'latitude', 'longitude'}))

    def test_find_model_latitude_variable_name(self):
        self.assertEqual('lat', self.data.find_model_latitude_variable_name())
        test_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/ogs_test_smaller.nc"
        data = Data(test_file)
        self.assertEqual('latitude', data.find_model_latitude_variable_name())

    def test_find_model_longitude_variable_name(self):
        self.assertEqual('lon', self.data.find_model_longitude_variable_name())
        test_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/ogs_test_smaller.nc"
        data = Data(test_file)
        self.assertEqual('longitude', data.find_model_longitude_variable_name())


    def test_var_access(self):
        chl_data = self.data.read_model('chl', [0, 0, 0, 0])
        self.assertAlmostEqual(0.1111, chl_data)


    def test_data_is_read_only_once_full_variable(self):
        self.data.read_model('chl')
        chl_data = self.data.read_model('chl', [0, 0, 0, 0])
        self.assertAlmostEqual(0.1111, chl_data)

        self.data.__getattribute__('chl')[0][0][0][0] = 0.5
        chl_data = self.data.read_model('chl', [0, 0, 0, 0])
        self.assertAlmostEqual(0.5, chl_data)


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
        test_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/ogs_test_smaller.nc"
        data = Data(test_file)
        self.assertEqual(1, len(data.ref_vars()))
        self.assertEqual('Ref_chl', data.ref_vars()[0])


    def test_caching(self):
        test_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/ogs_test_smaller.nc"
        data = Data(test_file, None, 0.05)
        data.read_model('chl')
        self.assertTrue(hasattr(data, 'chl'))
        data.read_model('dox')
        self.assertTrue(hasattr(data, 'dox'))
        self.assertFalse(hasattr(data, 'chl'))

        data = Data(test_file, None, 2)
        data.read_model('chl')
        self.assertTrue(hasattr(data, 'chl'))
        data.read_model('dox')
        self.assertTrue(hasattr(data, 'dox'))
        self.assertTrue(hasattr(data, 'chl'))


    def test_compute_variable_size(self):
        test_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/ogs_test_smaller.nc"
        data = Data(test_file)
        self.assertAlmostEqual(0.0250244140625, data.compute_variable_size('chl'))
        self.assertAlmostEqual(0.0250244140625, data.compute_variable_size('dox'))
        self.assertAlmostEqual(0.00030517578125, data.compute_variable_size('longitude'))

    def test_get_data(self):
        self.data.read_model('chl')
        array = self.data.get_data([0, 0, 0, 0], 'chl')
        assert_array_equal(np.array([0.1111], dtype='float32'), array)

        array = self.data.get_data([1, 0, 1, 2], 'chl')
        assert_array_equal(np.array([0.1223], dtype='float32'), array)
        array = self.data.get_data([1, 0, 1, 3], 'chl')
        assert_array_equal(np.array([0.2223], dtype='float32'), array)

    def test_has_gridded_ref_var(self):
        self.assertTrue(self.data.has_one_dim_ref_var())
        test_file = os.path.dirname(os.path.realpath(__file__)) + "/../resources/ogs_test_smaller.nc"
        data = Data(test_file)
        self.assertFalse(data.has_one_dim_ref_var())


    def test_get_differing_dim_names(self):
        data = DataMock()
        dim_indices = data.get_differing_dim_names('model_0', 'ref_0')
        self.assertDictEqual({}, dim_indices)

        dim_indices = data.get_differing_dim_names('model_0', 'ref_1')
        self.assertDictEqual({'depth': 'depth_ref'}, dim_indices)

        dim_indices = data.get_differing_dim_names('model_0', 'ref_2')
        self.assertDictEqual({'time': 'time_ref', 'depth': 'depth_ref'}, dim_indices)

        self.assertRaises(ValueError, lambda : data.get_differing_dim_names('model_0', 'ref_3'))


    def test_get_slices(self):
        data = DataMock()
        model_values_slices, ref_values_slices = data.get_slices('model_0', 'ref_1')
        self.assertListEqual([slice(None), slice(3, 4), slice(None), slice(None)], model_values_slices)
        self.assertListEqual([slice(0, 5), slice(0, 1), slice(0, 5), slice(0, 10)], ref_values_slices)


class DataMock(Data):

    def __init__(self):
        super().__init__(None)
        self._Data__model_file = None


    def _Data__dimension_string(self, ignored, var):
        if var == 'model_0':
            return 'time depth lat lon'
        elif var =='ref_0':
            return 'time depth lat lon'
        elif var == 'ref_1':
            return 'time depth_ref lat lon'
        elif var == 'ref_2':
            return 'time_ref depth_ref lat lon'
        elif var == 'ref_3':
            return 'depth_ref lat lon'


    def is_ref_data_split(self):
        return False


    def read_model(self, ignored_1, ignored_2=None):
        return [2, 3, 4, 5]


    def read_reference(self, ignored_1, ignored_2=None):
        return 5


    def get_model_dimensions(self, ignored=None):
        return ['time', 'depth', 'lat', 'lon']


    def get_reference_dimensions(self, ignored=None):
        return ['time', 'depth_ref', 'lat', 'lon']


    def ref_dim_size(self, dim_name):
        if dim_name == 'lon':
            return 10
        else:
            return 5