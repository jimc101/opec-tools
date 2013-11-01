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

from unittest import TestCase
import unittest
import numpy.testing as np
from opec.matchup_engine import normalise
from opec.configuration import Configuration
from opec.matchup_engine import MatchupEngine
from opec.data import Data
import os
from opec.reference_records_finder import ReferenceRecord, find_ref_coordinate_names

class MatchupEngine_test(TestCase):

    def setUp(self):
        self.path = os.path.dirname(os.path.realpath(__file__)) + '/../'
        self.data = Data(self.path + 'resources/test.nc')


    def tearDown(self):
        self.data.close()


    def test_find_pixel_positions_small_max_delta(self):
        me = MatchupEngine(self.data, Configuration())
        pixel_position = me.find_matchup_position(55, 6.0)
        np.assert_array_almost_equal((1, 0, 5.8, 55.2), pixel_position)


    def test_find_pixel_positions_huge_max_delta(self):
        me = MatchupEngine(self.data, Configuration())
        pixel_position = me.find_matchup_position(55, 6.0)
        np.assert_array_almost_equal((1, 0, 5.8, 55.2), pixel_position)


    def test_find_time_positions_huge_delta(self):
        me = MatchupEngine(self.data, Configuration(time_delta=100000))
        time_position = me.find_matchup_times(1261440250)[0]
        np.assert_array_almost_equal((0, 1261440000), time_position)


    def test_find_time_positions_small_delta(self):
        me = MatchupEngine(self.data, Configuration(time_delta=6))
        time_positions = me.find_matchup_times(1261447205)[0]
        np.assert_array_almost_equal((1, 1261447200), time_positions)


    def test_find_matchup(self):
        reference_record = ReferenceRecord(0, 55.1, 5.5, 1261440252, 0.0012)
        me = MatchupEngine(self.data, Configuration())
        matchups = me.find_matchups(reference_record)
        self.assertEqual(1, len(matchups))
        matchup = matchups[0]
        self.assertIsNotNone(matchup)
        self.assertEqual(55.1, matchup.reference_record.lat)
        self.assertEqual(5.5, matchup.reference_record.lon)
        self.assertEqual(1261440252, matchup.reference_record.time)
        self.assertEqual(0.0012, matchup.reference_record.depth)
        self.assertAlmostEqual(0.1111, matchup.get_model_value('chl', self.data), 5)
        self.assertAlmostEqual(1.1111, matchup.get_model_value('sst', self.data), 5)
        self.assertAlmostEqual(0.1, matchup.get_ref_value('chl_ref', self.data), 5)


    def test_find_matchups_single(self):
        reference_record = ReferenceRecord(0, 55.20123, 6.30048, 1261447205, 0.0020015)
        config = Configuration(time_delta=10, depth_delta=0.0001)
        me = MatchupEngine(self.data, config)
        matchups = me.find_matchups(reference_record)
        self.assertEqual(1, len(matchups))
        matchup = matchups[0]
        self.assertIsNotNone(matchup)
        self.assertAlmostEqual(55.20123, matchup.reference_record.lat)
        self.assertAlmostEqual(6.30048, matchup.reference_record.lon)
        self.assertAlmostEqual(1261447205, matchup.reference_record.time)
        self.assertAlmostEqual(0.0020015, matchup.reference_record.depth)


    def test_find_matchups_single_no_depth(self):
        data = Data(self.path + 'resources/test_without_depth.nc')
        config = Configuration(time_delta=10)
        me = MatchupEngine(data, config)

        reference_record = ReferenceRecord(0, 55.20123, 6.30048, 1261447205, None)
        matchups = me.find_matchups(reference_record)
        self.assertEqual(1, len(matchups))
        matchup = matchups[0]
        self.assertIsNotNone(matchup)
        self.assertAlmostEqual(55.20123, matchup.reference_record.lat)
        self.assertAlmostEqual(6.30048, matchup.reference_record.lon)
        self.assertAlmostEqual(1261447205, matchup.reference_record.time)
        self.assertIsNone(matchup.reference_record.depth)


    def test_find_ref_coordinate_names(self):
        ref_coord_variable_names = ['lat_ref', 'ref_lon', 'reftime']
        lat, lon, time, depth = find_ref_coordinate_names(ref_coord_variable_names)
        self.assertEqual('lat_ref', lat)
        self.assertEqual('ref_lon', lon)
        self.assertEqual('reftime', time)
        self.assertEqual(None, depth)


    def test_find_all_matchups(self):
        me = MatchupEngine(self.data, Configuration())
        all_matchups = me.find_all_matchups()
        self.assertIsNotNone(all_matchups)
        expected_matchup_count = 3 #reference_records
        self.assertEqual(expected_matchup_count, len(all_matchups))
        matchup = all_matchups[0]
        self.assertAlmostEqual(55.21, matchup.reference_record.lat, 5)
        self.assertAlmostEqual(5.31, matchup.reference_record.lon, 5)
        self.assertEqual(1261440250, matchup.reference_record.time)
        self.assertAlmostEqual(0.0012, matchup.reference_record.depth, 5)


    def test_normalise(self):
        self.assertEqual(type(3), type(normalise(2.5, 3)))
        self.assertEqual(3, normalise(10.5, 3))
        self.assertEqual(1, normalise(0.5, 10))
        self.assertEqual(3, normalise(2.500001, 10))
        self.assertEqual(2, normalise(2.499999, 10))


    def test_remove_empty_matchups(self):
        data = Data(self.path + 'resources/test_single_model_fill_values.nc')
        me = MatchupEngine(data)
        matchups = me.find_all_matchups()
        self.assertEqual(3, len(matchups))
        matchups = me.remove_empty_matchups(matchups)
        self.assertEqual(2, len(matchups))


    @unittest.skip('shall not run in production environment')
    def test_find_matchups_with_gridded_reference_variable(self):
        data = Data(self.path + 'resources/ogs_test_smaller.nc')
        me = MatchupEngine(data, Configuration())
        matchups = me.find_all_matchups()
        self.assertIsNotNone(matchups)
        self.assertEqual(6560, len(matchups))