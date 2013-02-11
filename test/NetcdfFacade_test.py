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

import os
import unittest
from numpy.core.numeric import array
from numpy.testing.utils import assert_array_equal
from numpy import nan
from opec.NetCDFFacade import NetCDFFacade

class NetCDFFacade_test(unittest.TestCase):

    def setUp(self):
        self.path = os.path.dirname(os.path.realpath(__file__)) + '/../'
        filename = 'resources/test.nc'
        self.netcdf = NetCDFFacade(self.path + filename)

    def tearDown(self):
        self.netcdf.close()

    def test_get_dim_size(self):
        self.assertEqual(2, self.netcdf.get_dim_size("time"))
        self.assertEqual(2, self.netcdf.get_dim_size("depth"))
        self.assertEqual(2, self.netcdf.get_dim_size("lat"))
        self.assertEqual(4, self.netcdf.get_dim_size("lon"))

    def test_get_global_attribute_value(self):
        self.assertEqual("some title", self.netcdf.get_global_attribute("title"))
        self.assertEqual("institution code", self.netcdf.get_global_attribute("institution"))
        self.assertEqual("links to references", self.netcdf.get_global_attribute("references"))
        self.assertEqual("method of production", self.netcdf.get_global_attribute("source"))
        self.assertEqual("CF-1.6", self.netcdf.get_global_attribute("Conventions"))
        self.assertEqual("audit trail", self.netcdf.get_global_attribute("history"))
        self.assertEqual("comment", self.netcdf.get_global_attribute("comment"))

    def test_get_variable_attribute(self):
        self.assertEqual("longitude", self.netcdf.get_variable_attribute("lon", "long_name"))
        self.assertAlmostEqual(-180.0, self.netcdf.get_variable_attribute("lon", "valid_min"), 5)

    def test_get_dimension_string(self):
        self.assertEqual("lon", self.netcdf.get_dimension_string("lon"))
        self.assertEqual("lat", self.netcdf.get_dimension_string("lat"))
        self.assertEqual("time", self.netcdf.get_dimension_string("time"))
        self.assertEqual("time depth lat lon", self.netcdf.get_dimension_string("chl"))

    def test_get_dim_length(self):
        self.assertEqual(2, self.netcdf.get_dim_length("chl", 0))
        self.assertEqual(2, self.netcdf.get_dim_length("chl", 1))
        self.assertEqual(2, self.netcdf.get_dim_length("chl", 2))
        self.assertEqual(4, self.netcdf.get_dim_length("chl", 3))

    def test_get_data_via_origin_and_shape(self):
        assert_array_equal(array([[[[0.1111]]]], dtype='float32'),
            self.netcdf.get_data("chl", [0, 0, 0, 0], [1, 1, 1, 1]))

        assert_array_equal(array([
            [
              [[ 0.1111, 0.2111], [ 0.1121, 0.2121]],
              [[ 0.1112, 0.2112], [ 0.1122, 0.2122]]
            ],
            [
              [[ 0.1113, 0.2113], [ 0.1123, 0.2123]],
              [[ 0.1114, 0.2114], [ 0.1124, 0.2124]]
            ]
        ],
            dtype='float32'), self.netcdf.get_data("chl", [0, 0, 0, 0], [2, 2, 2, 2]))


        assert_array_equal(array([
            [
              [[ 0.2111, 0.1211], [ 0.2121, 0.1221]],
            ],
        ],
            dtype='float32'), self.netcdf.get_data("chl", [0, 0, 0, 1], [1, 1, 2, 2]))

    def test_get_dimensions(self):
        assert_array_equal(["time", "depth", "lat", "lon", "record_num"], self.netcdf.get_dimensions())
        self.assertEqual(4, len(self.netcdf.get_dimensions('chl')))

    def test_get_model_variables(self):
        assert_array_equal(['chl', 'sst'], self.netcdf.get_model_variables())

    def test_get_reference_variables(self):
        assert_array_equal(['chl_ref'], self.netcdf.get_reference_variables())

    def test_get_gridded_reference_variables(self):
        filename = 'resources/ogs_test_smaller.nc'
        netcdf = NetCDFFacade(self.path + filename)
        self.assertEqual(1, len(netcdf.get_reference_variables()))
        self.assertEqual('Ref_chl', netcdf.get_reference_variables()[0])

    def test_get_reference_variable(self):
        self.assertIsNone(self.netcdf.get_reference_variable('sst_ref'))
        self.assertIsNotNone(self.netcdf.get_reference_variable('chl_ref'))

    def test_read_variable_fully(self):
        fullyReadChl = self.netcdf.read_variable_fully('chl')
        assert_array_equal(
            array(
            [[[[0.1111, 0.2111, 0.1211, 0.2211],
               [0.1121, 0.2121, 0.1221, 0.2221]],
              [[0.1112, 0.2112, 0.1212, 0.2212],
               [0.1122, 0.2122, 0.1222, 0.2222]]],
             [[[0.1113, 0.2113, 0.1213, 0.2213],
               [0.1123, 0.2123, 0.1223, 0.2223]],
              [[0.1114, 0.2114, 0.1214, 0.2214],
               [0.1124, 0.2124, 0.1224, 0.2224]]]], dtype='float32'),
            fullyReadChl)

    def test_get_variable_size(self):
        self.assertEqual(2, self.netcdf.get_variable_size('lat'))
        self.assertEqual(4, self.netcdf.get_variable_size('lon'))
        self.assertEqual(2, self.netcdf.get_variable_size('time'))
        self.assertEqual(32, self.netcdf.get_variable_size('chl'))
        self.assertEqual(32, self.netcdf.get_variable_size('sst'))
        self.assertEqual(32, self.netcdf.get_variable_size('sst'))
        self.assertEqual(3, self.netcdf.get_variable_size('chl_ref'))

    def test_get_coordinate_variables(self):
        coordinate_variables = self.netcdf.get_coordinate_variables()
        self.assertEqual(4, len(coordinate_variables))
        self.assertTrue('lat' in coordinate_variables)
        self.assertTrue('lon' in coordinate_variables)
        self.assertTrue('time' in coordinate_variables)
        self.assertTrue('depth' in coordinate_variables)

    def test_get_ref_coordinate_variables(self):
        ref_coordinate_variables = self.netcdf.get_ref_coordinate_variables()
        self.assertEqual(4, len(ref_coordinate_variables))
        self.assertEqual('time_ref', ref_coordinate_variables[0])
        self.assertEqual('depth_ref', ref_coordinate_variables[1])
        self.assertEqual('lat_ref', ref_coordinate_variables[2])
        self.assertEqual('lon_ref', ref_coordinate_variables[3])

    def test_get_ref_coordinate_variables_empty(self):
        netcdf = NetCDFFacade(self.path + 'resources/test_without_records.nc')
        self.assertEqual(0, len(netcdf.get_reference_variables()))
        ref_coordinate_variables = netcdf.get_ref_coordinate_variables()
        self.assertEqual(0, len(ref_coordinate_variables))

    def test_has_model_dimension(self):
        self.assertTrue(self.netcdf.has_model_dimension('time'))
        self.assertTrue(self.netcdf.has_model_dimension('depth'))
        self.assertFalse(self.netcdf.has_model_dimension('kaesemauken'))

    def test_change_variable_values(self):
        chl = self.netcdf.get_variable('chl')
        self.assertAlmostEqual(0.1111, chl[:][0][0][0][0])

        chl[0][0][0][0] = nan
        self.assertAlmostEqual(0.1111, chl[:][0][0][0][0])
