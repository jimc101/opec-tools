from unittest import TestCase
import numpy.testing as np
from src.main.python.MatchupEngine import MatchupEngine, ReferenceRecord, find_ref_coordinate_names
from src.main.python.Data import Data

class MatchupEngineTest(TestCase):

    def setUp(self):
        self.data = Data('../resources/test.nc')
        self.me = MatchupEngine(self.data)

    def tearDown(self):
        self.data.close()

    def test_find_pixel_positions_macro_pixel_size_3_small_max_delta(self):
        pixel_positions = self.me.find_matchup_positions(55, 6.0, 3, 0.1)
        self.assertEqual(1, len(pixel_positions))
        np.assert_array_almost_equal((1, 0, 5.8, 55.2), pixel_positions[0])

    def test_find_pixel_positions_macro_pixel_size_3_huge_max_delta(self):
        pixel_positions = self.me.find_matchup_positions(55, 6.0, 3, 200)
        self.assertEqual(6, len(pixel_positions))
        np.assert_array_almost_equal((0, 0, 5.3, 55.2), pixel_positions[0])
        np.assert_array_almost_equal((0, 1, 5.3, 56.8), pixel_positions[1])
        np.assert_array_almost_equal((1, 0, 5.8, 55.2), pixel_positions[2])
        np.assert_array_almost_equal((1, 1, 5.8, 56.8), pixel_positions[3])
        np.assert_array_almost_equal((2, 0, 6.3, 55.2), pixel_positions[4])
        np.assert_array_almost_equal((2, 1, 6.3, 56.8), pixel_positions[5])

    def test_find_pixel_positions_macro_pixel_size_5_small_max_delta(self):
        pixel_positions = self.me.find_matchup_positions(55, 6.0, 5, 0.1)
        self.assertEqual(1, len(pixel_positions))
        np.assert_array_almost_equal((1, 0, 5.8, 55.2), pixel_positions[0])

    def test_find_pixel_positions_macro_pixel_size_5_huge_max_delta(self):
        pixel_positions = self.me.find_matchup_positions(55, 6.0, 5, 200)
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
        time_positions = self.me.find_matchup_times(1261440250, 100000)
        self.assertEqual(2, len(time_positions))
        np.assert_array_almost_equal((0, 1261440000), time_positions[0])
        np.assert_array_almost_equal((1, 1261447200), time_positions[1])

    def test_find_time_positions_small_delta(self):
        time_positions = self.me.find_matchup_times(1261447205, 6)
        self.assertEqual(1, len(time_positions))
        np.assert_array_almost_equal((1, 1261447200), time_positions[0])

    def test_delta(self):
        self.assertAlmostEqual(0.13, self.me.delta(55.2, 5.3, 55, 5))
        self.assertAlmostEqual(6.48, self.me.delta(56.8, 6.8, 55, 5))

    def test_find_matchups_all(self):
        reference_record = ReferenceRecord('chl', 0.1, 55.1, 5.5, 1261440252, 0.0012)
        matchups = self.me.find_matchups(reference_record, None, 7)
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
        matchups = self.me.find_matchups(reference_record, None, 7, 0.1, 10, 0.0001)
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
        self.data = Data('../resources/test_without_depth.nc')
        self.me = MatchupEngine(self.data)

        reference_record = ReferenceRecord('chl_ref', 1234.5678, 55.20123, 6.30048, 1261447205, None)
        matchups = self.me.find_matchups(reference_record, 'chl', 7, 0.1, 10)
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
        reference_records = self.me.find_reference_records('chl_ref')
        self.assertEqual(3, len(reference_records))
        reference_records = self.me.find_reference_records('sst_ref')
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
        all_matchups = self.me.find_all_matchups(ref_variable_name, model_variable_name, 9)
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