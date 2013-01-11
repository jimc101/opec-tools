import logging
from unittest import TestCase
import math
import numpy.testing as np
from src.main.python.Configuration import Configuration
from src.main.python.MatchupEngine import MatchupEngine, ReferenceRecord, find_ref_coordinate_names, delta, normalise
from src.main.python.Data import Data

class MatchupEngineTest(TestCase):

    def setUp(self):
        self.data = Data('../resources/test.nc')
        logging.basicConfig(level=logging.DEBUG)


    def tearDown(self):
        logging.basicConfig(level=logging.WARNING)
        self.data.close()

    def test_find_matchups_default_config(self):
        me = MatchupEngine(self.data)
        matchups = me.find_all_matchups('chl_ref', 'chl')
        self.assertIsNotNone(matchups)

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
        reference_record = ReferenceRecord('chl', 0.1, 55.1, 5.5, 1261440252, 0.0012)
        me = MatchupEngine(self.data, Configuration(macro_pixel_size=7, geo_delta=10))
        matchups = me.find_matchups(reference_record, None)
        self.assertIsNotNone(matchups)
        self.assertEqual(32, len(matchups))
        matchup = matchups[0]
        self.assertEqual(55.1, matchup.ref_lat)
        self.assertEqual(5.5, matchup.ref_lon)
        self.assertEqual(1261440252, matchup.ref_time)
        self.assertEqual(0.0012, matchup.ref_depth)

        self.assertAlmostEqual(0.1, matchup.lat_delta, 5)
        self.assertAlmostEqual(0.2, matchup.lon_delta, 5)
        self.assertEqual(252, matchup.time_delta)
        self.assertAlmostEqual(0.0002, matchup.depth_delta, 5)

        self.assertAlmostEqual(0.1111, matchup.model_value)
        self.assertAlmostEqual(0.1, matchup.ref_value)

    def test_find_matchups_single(self):
        reference_record = ReferenceRecord('chl', 1234.5678, 55.20123, 6.30048, 1261447205, 0.0020015)
        config = Configuration(macro_pixel_size=7, geo_delta=0.1, time_delta=10, depth_delta=0.0001)
        me = MatchupEngine(self.data, config)
        matchups = me.find_matchups(reference_record, None)
        self.assertIsNotNone(matchups)
        self.assertEqual(1, len(matchups))
        matchup = matchups[0]
        self.assertAlmostEqual(55.20123, matchup.ref_lat)
        self.assertAlmostEqual(6.30048, matchup.ref_lon)
        self.assertAlmostEqual(1261447205, matchup.ref_time)
        self.assertAlmostEqual(0.0020015, matchup.ref_depth)

        self.assertAlmostEqual(0.00123, matchup.lat_delta, 5)
        self.assertAlmostEqual(0.00048, matchup.lon_delta, 5)
        self.assertEqual(5, matchup.time_delta)
        self.assertAlmostEqual(0.0000015, matchup.depth_delta, 7)

        self.assertAlmostEqual(1234.5678, matchup.ref_value)
        self.assertAlmostEqual(0.1214, matchup.model_value)

    def test_find_matchups_single_no_depth(self):
        data = Data('../resources/test_without_depth.nc')
        config = Configuration(macro_pixel_size=7, geo_delta=0.1, time_delta=10)
        me = MatchupEngine(data, config)

        reference_record = ReferenceRecord('chl_ref', 1234.5678, 55.20123, 6.30048, 1261447205, None)
        matchups = me.find_matchups(reference_record, 'chl')
        self.assertIsNotNone(matchups)
        self.assertEqual(1, len(matchups))
        matchup = matchups[0]
        self.assertAlmostEqual(55.20123, matchup.ref_lat)
        self.assertAlmostEqual(6.30048, matchup.ref_lon)
        self.assertAlmostEqual(1261447205, matchup.ref_time)
        self.assertIsNone(matchup.ref_depth)

        self.assertAlmostEqual(0.00123, matchup.lat_delta, 5)
        self.assertAlmostEqual(0.00048, matchup.lon_delta, 5)
        self.assertEqual(5, matchup.time_delta)
        self.assertIsNone(matchup.depth_delta, 7)

        self.assertAlmostEqual(1234.5678, matchup.ref_value)
        self.assertAlmostEqual(0.213, matchup.model_value)

    def test_find_reference_records(self):
        me = MatchupEngine(self.data)
        reference_records = me.find_reference_records('chl_ref')
        self.assertEqual(3, len(reference_records))
        reference_records = me.find_reference_records('sst_ref')
        self.assertEqual(0, len(reference_records))

    def test_find_reference_records_no_depth(self):
        self.data = Data('../resources/test_without_depth.nc')
        self.me = MatchupEngine(self.data)
        reference_records = self.me.find_reference_records('chl_ref')
        self.assertEqual(3, len(reference_records))
        reference_records = self.me.find_reference_records('sst_ref')
        self.assertEqual(0, len(reference_records))

    def test_find_ref_coordinate_names(self):
        ref_coord_variable_names = ['lat_ref', 'ref_lon', 'reftime']
        lat, lon, time, depth = find_ref_coordinate_names(ref_coord_variable_names)
        self.assertEqual('lat_ref', lat)
        self.assertEqual('ref_lon', lon)
        self.assertEqual('reftime', time)
        self.assertEqual(None, depth)

    def test_find_all_matchups(self):
        ref_variable_name = 'chl_ref'
        model_variable_name = 'chl'
        me = MatchupEngine(self.data, Configuration(macro_pixel_size=9, geo_delta=10))
        all_matchups = me.find_all_matchups(ref_variable_name, model_variable_name)
        self.assertIsNotNone(all_matchups)
        expected_matchup_count = 2 * 2 * 2 * 4 * 3 # time * depth * lat * lon * #reference_records
        self.assertEqual(expected_matchup_count, len(all_matchups))
        matchup = all_matchups[0]
        self.assertAlmostEqual(55.21, matchup.ref_lat, 5)
        self.assertAlmostEqual(5.31, matchup.ref_lon, 5)
        self.assertEqual(1261440250, matchup.ref_time)
        self.assertAlmostEqual(0.0012, matchup.ref_depth, 5)

        self.assertAlmostEqual(0.01, matchup.lat_delta, 5)
        self.assertAlmostEqual(0.01, matchup.lon_delta, 5)
        self.assertEqual(250, matchup.time_delta)
        self.assertAlmostEqual(0.0002, matchup.depth_delta, 5)

        self.assertAlmostEqual(0.1111, matchup.model_value)
        self.assertAlmostEqual(0.1, matchup.ref_value)

    def test_find_matchups_in_file_containing_fill_values(self):
        config = Configuration(macro_pixel_size=1, geo_delta=10, time_delta=1000, depth_delta=0.00021)
        data = Data('../resources/test_including_fill_values.nc')
        me = MatchupEngine(data, config)
        all_matchups = me.find_all_matchups('chl_ref', 'chl')
        self.assertEqual(0, len(all_matchups))

        config = Configuration(macro_pixel_size=11, geo_delta=10, time_delta=86400, depth_delta=10)
        me = MatchupEngine(data, config)
        all_matchups = me.find_all_matchups('chl_ref', 'chl')
        self.assertEqual(60, len(all_matchups))

    def test_normalise(self):
        self.assertEqual(type(3), type(normalise(2.5, 3)))
        self.assertEqual(3, normalise(10.5, 3))
        self.assertEqual(1, normalise(0.5, 10))
        self.assertEqual(3, normalise(2.500001, 10))
        self.assertEqual(2, normalise(2.499999, 10))

    def test_that_data_manipulations_are_conserved(self):
        self.data.read('chl')
        chl_data = self.data['chl']
        self.assertAlmostEqual(0.1111, chl_data[0][0][0][0])

        config = Configuration(macro_pixel_size=1, geo_delta=0.01415, time_delta=3000, depth_delta=0.0003)
        me = MatchupEngine(self.data, config)
        matchup = me.find_all_matchups('chl_ref', 'chl')[0]

        self.assertAlmostEqual(0.1111, matchup.model_value)
        self.assertAlmostEqual(0.1, matchup.ref_value)

        self.data['chl'][0][0][0][0] = 0.2
        self.data['chl_ref'][0] = 0.3

        matchup = me.find_all_matchups('chl_ref', 'chl')[0]

        self.assertAlmostEqual(0.2, matchup.model_value)
        self.assertAlmostEqual(0.3, matchup.ref_value)