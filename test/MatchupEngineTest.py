import logging
from unittest import TestCase
import math
import numpy.testing as np
from opec.MatchupEngine import ReferenceRecord, find_ref_coordinate_names, delta, normalise
from opec.Configuration import Configuration
from opec.MatchupEngine import MatchupEngine
from opec.Data import Data
import os

class MatchupEngineTest(TestCase):

    @classmethod
    def setUpClass(self):
        self.cwd = os.getcwd()
        os.chdir('..')

    @classmethod
    def tearDownClass(self):
        os.chdir(self.cwd)

    def setUp(self):
        self.data = Data('resources/test.nc')
        logging.basicConfig(level=logging.DEBUG)

    def tearDown(self):
        logging.basicConfig(level=logging.WARNING)
        self.data.close()

    def test_find_pixel_positions_macro_pixel_size_3_small_max_delta(self):
        me = MatchupEngine(self.data, Configuration(macro_pixel_size=3, geo_delta=0.3))
        pixel_positions = me.find_matchup_positions(55, 6.0)
        self.assertEqual(1, len(pixel_positions))
        np.assert_array_almost_equal((1, 0, 5.8, 55.2), pixel_positions[0])

    def test_find_pixel_positions_macro_pixel_size_3_huge_max_delta(self):
        me = MatchupEngine(self.data, Configuration(macro_pixel_size=3, geo_delta=200))
        pixel_positions = me.find_matchup_positions(55, 6.0)
        self.assertEqual(6, len(pixel_positions))
        np.assert_array_almost_equal((0, 0, 5.3, 55.2), pixel_positions[0])
        np.assert_array_almost_equal((0, 1, 5.3, 56.8), pixel_positions[1])
        np.assert_array_almost_equal((1, 0, 5.8, 55.2), pixel_positions[2])
        np.assert_array_almost_equal((1, 1, 5.8, 56.8), pixel_positions[3])
        np.assert_array_almost_equal((2, 0, 6.3, 55.2), pixel_positions[4])
        np.assert_array_almost_equal((2, 1, 6.3, 56.8), pixel_positions[5])

    def test_find_pixel_positions_macro_pixel_size_5_small_max_delta(self):
        me = MatchupEngine(self.data, Configuration(macro_pixel_size=5, geo_delta=0.3))
        pixel_positions = me.find_matchup_positions(55, 6.0)
        self.assertEqual(1, len(pixel_positions))
        np.assert_array_almost_equal((1, 0, 5.8, 55.2), pixel_positions[0])

    def test_find_pixel_positions_macro_pixel_size_5_huge_max_delta(self):
        me = MatchupEngine(self.data, Configuration(macro_pixel_size=5, geo_delta=200))
        pixel_positions = me.find_matchup_positions(55, 6.0)
        self.assertEqual(8, len(pixel_positions))
        np.assert_array_almost_equal((0, 0, 5.3, 55.2), pixel_positions[0])
        np.assert_array_almost_equal((0, 0, 5.3, 55.2), pixel_positions[0])
        np.assert_array_almost_equal((0, 1, 5.3, 56.8), pixel_positions[1])
        np.assert_array_almost_equal((1, 0, 5.8, 55.2), pixel_positions[2])
        np.assert_array_almost_equal((1, 1, 5.8, 56.8), pixel_positions[3])
        np.assert_array_almost_equal((2, 0, 6.3, 55.2), pixel_positions[4])
        np.assert_array_almost_equal((2, 1, 6.3, 56.8), pixel_positions[5])
        np.assert_array_almost_equal((3, 0, 6.8, 55.2), pixel_positions[6])
        np.assert_array_almost_equal((3, 1, 6.8, 56.8), pixel_positions[7])

    def test_find_time_positions_huge_delta(self):
        me = MatchupEngine(self.data, Configuration(time_delta=100000))
        time_positions = me.find_matchup_times(1261440250)
        self.assertEqual(2, len(time_positions))
        np.assert_array_almost_equal((0, 1261440000), time_positions[0])
        np.assert_array_almost_equal((1, 1261447200), time_positions[1])

    def test_find_time_positions_small_delta(self):
        me = MatchupEngine(self.data, Configuration(time_delta=6))
        time_positions = me.find_matchup_times(1261447205)
        self.assertEqual(1, len(time_positions))
        np.assert_array_almost_equal((1, 1261447200), time_positions[0])

    def test_delta(self):
        self.assertAlmostEqual(math.sqrt(0.13), delta(55.2, 5.3, 55, 5))
        self.assertAlmostEqual(math.sqrt(6.48), delta(56.8, 6.8, 55, 5))

    def test_find_matchups_all(self):
        reference_record = ReferenceRecord(0, 55.1, 5.5, 1261440252, 0.0012)
        me = MatchupEngine(self.data, Configuration(macro_pixel_size=7, geo_delta=10))
        matchups = me.find_matchups(reference_record)
        self.assertIsNotNone(matchups)
        self.assertEqual(32, len(matchups))
        matchup = matchups[0]
        self.assertEqual(55.1, matchup.reference_record.lat)
        self.assertEqual(5.5, matchup.reference_record.lon)
        self.assertEqual(1261440252, matchup.reference_record.time)
        self.assertEqual(0.0012, matchup.reference_record.depth)

    def test_find_matchups_single(self):
        reference_record = ReferenceRecord(0, 55.20123, 6.30048, 1261447205, 0.0020015)
        config = Configuration(macro_pixel_size=7, geo_delta=0.1, time_delta=10, depth_delta=0.0001)
        me = MatchupEngine(self.data, config)
        matchups = me.find_matchups(reference_record)
        self.assertIsNotNone(matchups)
        self.assertEqual(1, len(matchups))
        matchup = matchups[0]
        self.assertAlmostEqual(55.20123, matchup.reference_record.lat)
        self.assertAlmostEqual(6.30048, matchup.reference_record.lon)
        self.assertAlmostEqual(1261447205, matchup.reference_record.time)
        self.assertAlmostEqual(0.0020015, matchup.reference_record.depth)

    def test_find_matchups_single_no_depth(self):
        data = Data('resources/test_without_depth.nc')
        config = Configuration(macro_pixel_size=7, geo_delta=0.1, time_delta=10)
        me = MatchupEngine(data, config)

        reference_record = ReferenceRecord(0, 55.20123, 6.30048, 1261447205, None)
        matchups = me.find_matchups(reference_record)
        self.assertIsNotNone(matchups)
        self.assertEqual(1, len(matchups))
        matchup = matchups[0]
        self.assertAlmostEqual(55.20123, matchup.reference_record.lat)
        self.assertAlmostEqual(6.30048, matchup.reference_record.lon)
        self.assertAlmostEqual(1261447205, matchup.reference_record.time)
        self.assertIsNone(matchup.reference_record.depth)

    def test_find_reference_records(self):
        me = MatchupEngine(self.data)
        reference_records = me.find_reference_records()
        self.assertEqual(3, len(reference_records))
        self.assertAlmostEqual(55.21, reference_records[0].lat, 4)
        self.assertAlmostEqual(55.8, reference_records[1].lat, 4)
        self.assertAlmostEqual(56.12, reference_records[2].lat, 4)

        self.assertAlmostEqual(5.31, reference_records[0].lon, 4)
        self.assertAlmostEqual(5.72, reference_records[1].lon, 4)
        self.assertAlmostEqual(12.35, reference_records[2].lon, 4)

    def test_find_reference_records_no_depth(self):
        self.data = Data('resources/test_without_depth.nc')
        self.me = MatchupEngine(self.data)
        reference_records = self.me.find_reference_records()
        self.assertEqual(3, len(reference_records))

    def test_find_ref_coordinate_names(self):
        ref_coord_variable_names = ['lat_ref', 'ref_lon', 'reftime']
        lat, lon, time, depth = find_ref_coordinate_names(ref_coord_variable_names)
        self.assertEqual('lat_ref', lat)
        self.assertEqual('ref_lon', lon)
        self.assertEqual('reftime', time)
        self.assertEqual(None, depth)

    def test_find_all_matchups(self):
        me = MatchupEngine(self.data, Configuration(macro_pixel_size=9, geo_delta=10))
        all_matchups = me.find_all_matchups()
        self.assertIsNotNone(all_matchups)
        expected_matchup_count = 2 * 2 * 2 * 4 * 3 # time * depth * lat * lon * #reference_records
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