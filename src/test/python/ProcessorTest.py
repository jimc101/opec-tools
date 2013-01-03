from unittest import TestCase
import numpy as np
import numpy.ma as ma
from numpy.testing import assert_array_equal
from src.main.python.Data import Data
from src.main.python.MatchupEngine import MatchupEngine
from src.main.python.Processor import basic_statistics, harmonise

class ProcessorTest(TestCase):

    def setUp(self):
        self.data = Data('../resources/test.nc')
        self.me = MatchupEngine(self.data)

    def tearDown(self):
        self.data.close()

    def test_compute_basic_statistics_for_matchups(self):
        matchups = self.me.find_all_matchups('chl_ref', 'chl', 3)
        basic_stats = basic_statistics(matchups)
        self.assertAlmostEqual(0.0960456, basic_stats['rmsd'], 5)
        self.assertAlmostEqual(0.0868041, basic_stats['unbiased_rmsd'], 5)
        self.assertAlmostEqual(20.553573, basic_stats['pbias'], 5)
        self.assertAlmostEqual(0.0411071, basic_stats['bias'], 5)
        self.assertAlmostEqual(0.077279, basic_stats['corrcoeff'], 5)
        self.assertAlmostEqual(1.2662666, basic_stats['reliability_index'], 5)
        self.assertAlmostEqual(-0.6143319, basic_stats['model_efficiency'], 5)
        self.assertAlmostEqual(0.158892, basic_stats['mean'], 5)
        self.assertAlmostEqual(0.2, basic_stats['ref_mean'], 5)
        self.assertAlmostEqual(0.048909, basic_stats['stddev'], 5)
        self.assertAlmostEqual(0.075593, basic_stats['ref_stddev'], 5)
        self.assertAlmostEqual(0.12225, basic_stats['median'], 5)
        self.assertAlmostEqual(0.2, basic_stats['ref_median'], 5)
        self.assertAlmostEqual(0.22125, basic_stats['p90'], 5)
        self.assertAlmostEqual(0.3, basic_stats['ref_p90'], 5)
        self.assertAlmostEqual(0.222125, basic_stats['p95'], 5)
        self.assertAlmostEqual(0.3, basic_stats['ref_p95'], 5)
        self.assertAlmostEqual(0.1111, basic_stats['min'], 5)
        self.assertAlmostEqual(0.1, basic_stats['ref_min'], 5)
        self.assertAlmostEqual(0.2224, basic_stats['max'], 5)
        self.assertAlmostEqual(0.3, basic_stats['ref_max'], 5)

        self.assertAlmostEqual(basic_stats['rmsd'] ** 2, basic_stats['bias'] ** 2 + basic_stats['unbiased_rmsd'] ** 2, 5)

    def test_compute_basic_statistics(self):
        model_values = np.array(range(1, 5, 1)) # [1, 2, 3, 4]
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        basic_stats = basic_statistics(reference_values=ref_values, model_values=model_values)
        self.assertAlmostEqual(0.192028, basic_stats['unbiased_rmsd'], 5)
        self.assertAlmostEqual(0.193649, basic_stats['rmsd'], 5)
        self.assertAlmostEqual(-1.0101, basic_stats['pbias'], 5)
        self.assertAlmostEqual(-0.025, basic_stats['bias'], 5)
        self.assertAlmostEqual(0.99519, basic_stats['corrcoeff'], 5)
        self.assertAlmostEqual(1.03521, basic_stats['reliability_index'], 5)
        self.assertAlmostEqual(0.9588759, basic_stats['model_efficiency'], 5)
        self.assertAlmostEqual(2.5, basic_stats['mean'], 5)
        self.assertAlmostEqual(2.475, basic_stats['ref_mean'], 5)
        self.assertAlmostEqual(1.11803, basic_stats['stddev'], 5)
        self.assertAlmostEqual(0.954921, basic_stats['ref_stddev'], 5)
        self.assertAlmostEqual(2.5, basic_stats['median'], 5)
        self.assertAlmostEqual(2.55, basic_stats['ref_median'], 5)
        self.assertAlmostEqual(3.7, basic_stats['p90'], 5)
        self.assertAlmostEqual(3.46, basic_stats['ref_p90'], 5)
        self.assertAlmostEqual(3.85, basic_stats['p95'], 5)
        self.assertAlmostEqual(3.58, basic_stats['ref_p95'], 5)
        self.assertAlmostEqual(1, basic_stats['min'], 5)
        self.assertAlmostEqual(1.1, basic_stats['ref_min'], 5)
        self.assertAlmostEqual(4, basic_stats['max'], 5)
        self.assertAlmostEqual(3.7, basic_stats['ref_max'], 5)

        self.assertAlmostEqual(basic_stats['rmsd'] ** 2, basic_stats['bias'] ** 2 + basic_stats['unbiased_rmsd'] ** 2, 5)

    def test_compute_basic_statistics_with_masked_values(self):
        model_values = ma.array(np.arange(1.0, 5.0, 1), mask=np.array([False, False, True, False])) # [1, 2, --, 4]
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        basic_stats = basic_statistics(reference_values=ref_values, model_values=model_values)
        self.assertAlmostEqual(0.216024, basic_stats['unbiased_rmsd'], 5)
        self.assertAlmostEqual(0.216024, basic_stats['rmsd'], 5)
        self.assertAlmostEqual(6.344131e-15, basic_stats['pbias'], 5)
        self.assertAlmostEqual(0.0, basic_stats['bias'], 5)
        self.assertAlmostEqual(0.99484975, basic_stats['corrcoeff'], 5)
        self.assertAlmostEqual(1.039815, basic_stats['reliability_index'], 5)
        self.assertAlmostEqual(0.9589041, basic_stats['model_efficiency'], 5)
        self.assertAlmostEqual(2.3333333, basic_stats['mean'], 5)
        self.assertAlmostEqual(2.3333333, basic_stats['ref_mean'], 5)
        self.assertAlmostEqual(1.24722, basic_stats['stddev'], 5)
        self.assertAlmostEqual(1.06562, basic_stats['ref_stddev'], 5)
        self.assertAlmostEqual(2, basic_stats['median'], 5)
        self.assertAlmostEqual(2.2, basic_stats['ref_median'], 5)
        self.assertAlmostEqual(3.6, basic_stats['p90'], 5)
        self.assertAlmostEqual(3.4, basic_stats['ref_p90'], 5)
        self.assertAlmostEqual(3.8, basic_stats['p95'], 5)
        self.assertAlmostEqual(3.55, basic_stats['ref_p95'], 5)
        self.assertAlmostEqual(1, basic_stats['min'], 5)
        self.assertAlmostEqual(1.1, basic_stats['ref_min'], 5)
        self.assertAlmostEqual(4, basic_stats['max'], 5)
        self.assertAlmostEqual(3.7, basic_stats['ref_max'], 5)

        self.assertAlmostEqual(basic_stats['rmsd'] ** 2, basic_stats['bias'] ** 2 + basic_stats['unbiased_rmsd'] ** 2, 5)

    def test_compute_basic_statistics_with_extreme_model_values(self):
        model_values = np.array(range(1, 5, 1)) # [1, 2, 3, 4]
        ref_values = np.array([1, 1, 1, 1])
        basic_stats = basic_statistics(reference_values=ref_values, model_values=model_values)
        self.assertAlmostEqual(1.118034, basic_stats['unbiased_rmsd'], 5)
        self.assertAlmostEqual(1.870829, basic_stats['rmsd'], 5)
        self.assertAlmostEqual(-150, basic_stats['pbias'], 5)
        self.assertAlmostEqual(-1.5, basic_stats['bias'], 5)
        self.assertTrue(np.isnan(basic_stats['corrcoeff']))
        self.assertAlmostEqual(1.5106421, basic_stats['reliability_index'], 5)
        self.assertTrue(np.isnan(basic_stats['model_efficiency']))
        self.assertAlmostEqual(2.5, basic_stats['mean'], 5)
        self.assertAlmostEqual(1, basic_stats['ref_mean'], 5)
        self.assertAlmostEqual(1.11803, basic_stats['stddev'], 5)
        self.assertAlmostEqual(0.0, basic_stats['ref_stddev'], 5)
        self.assertAlmostEqual(2.5, basic_stats['median'], 5)
        self.assertAlmostEqual(1, basic_stats['ref_median'], 5)
        self.assertAlmostEqual(3.7, basic_stats['p90'], 5)
        self.assertAlmostEqual(1, basic_stats['ref_p90'], 5)
        self.assertAlmostEqual(3.85, basic_stats['p95'], 5)
        self.assertAlmostEqual(1, basic_stats['ref_p95'], 5)
        self.assertAlmostEqual(1, basic_stats['min'], 5)
        self.assertAlmostEqual(1, basic_stats['ref_min'], 5)
        self.assertAlmostEqual(4, basic_stats['max'], 5)
        self.assertAlmostEqual(1, basic_stats['ref_max'], 5)

        self.assertAlmostEqual(basic_stats['rmsd'] ** 2, basic_stats['bias'] ** 2 + basic_stats['unbiased_rmsd'] ** 2, 5)

    def test_compute_basic_statistics_with_extreme_reference_values(self):
        model_values = np.array([1, 1, 1, 1])
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        basic_stats = basic_statistics(reference_values=ref_values, model_values=model_values)
        self.assertAlmostEqual(0.954921, basic_stats['unbiased_rmsd'], 5)
        self.assertAlmostEqual(1.757128, basic_stats['rmsd'], 5)
        self.assertAlmostEqual(59.595959, basic_stats['pbias'], 5)
        self.assertAlmostEqual(1.475, basic_stats['bias'], 5)
        self.assertTrue(np.isnan(basic_stats['corrcoeff']))
        self.assertAlmostEqual(1.49908579, basic_stats['reliability_index'], 5)
        self.assertAlmostEqual(-2.38588, basic_stats['model_efficiency'], 5)
        self.assertAlmostEqual(1.0, basic_stats['mean'], 5)
        self.assertAlmostEqual(2.475, basic_stats['ref_mean'], 5)
        self.assertAlmostEqual(0, basic_stats['stddev'], 5)
        self.assertAlmostEqual(0.954921, basic_stats['ref_stddev'], 5)
        self.assertAlmostEqual(1, basic_stats['median'], 5)
        self.assertAlmostEqual(2.545, basic_stats['ref_median'], 2)
        self.assertAlmostEqual(1, basic_stats['p90'], 5)
        self.assertAlmostEqual(3.46, basic_stats['ref_p90'], 5)
        self.assertAlmostEqual(1, basic_stats['p95'], 5)
        self.assertAlmostEqual(3.58, basic_stats['ref_p95'], 2)
        self.assertAlmostEqual(1, basic_stats['min'], 5)
        self.assertAlmostEqual(1.1, basic_stats['ref_min'], 5)
        self.assertAlmostEqual(1, basic_stats['max'], 5)
        self.assertAlmostEqual(3.7, basic_stats['ref_max'], 5)

        self.assertAlmostEqual(basic_stats['rmsd'] ** 2, basic_stats['bias'] ** 2 + basic_stats['unbiased_rmsd'] ** 2, 5)

    def test_cleanup_1(self):
        model_values = ma.array(np.arange(1.0, 5.0, 1), mask=np.array([False, False, True, False])) # [1, --, 3, 4]
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        ref_values, model_values = harmonise(ref_values, model_values)

        # Note: assert_array_equals does not tests if masks are equal
        # and there is no dedicated method for this
        # so masks need to be tested separately

        assert_array_equal(np.array([1, 2, 3, 4]), model_values)
        assert_array_equal(np.array([False, False, True, False]), model_values.mask)

        assert_array_equal(np.array([1.1, 2.2, 2.9, 3.7]), ref_values)
        assert_array_equal(np.array([False, False, True, False]), ref_values.mask)

    def test_cleanup_2(self):
        model_values = np.array(np.arange(1.0, 5.0, 1)) # [1, 2, 3, 4]
        ref_values = ma.array(np.array([1.1, 2.2, 2.9, 3.7]), mask=np.array([True, False, False, False]))
        ref_values, model_values = harmonise(ref_values, model_values)

        # Note: assert_array_equals does not tests if masks are equal
        # and there is no dedicated method for this
        # so masks need to be tested separately

        assert_array_equal(np.array([1, 2, 3, 4]), model_values)
        assert_array_equal(np.array([True, False, False, False]), model_values.mask)

        assert_array_equal(np.array([1.1, 2.2, 2.9, 3.7]), ref_values)
        assert_array_equal(np.array([True, False, False, False]), ref_values.mask)

    def test_cleanup_3(self):
        model_values = ma.array(np.arange(1.0, 5.0, 1), mask=np.array([False, False, True, False])) # [1, 2, --, 4]
        ref_values = ma.array([1.1, 2.2, 2.9, 3.7], mask=np.array([True, False, False, False]))
        ref_values, model_values = harmonise(ref_values, model_values)

        # Note: assert_array_equals does not tests if masks are equal
        # and there is no dedicated method for this
        # so masks need to be tested separately

        assert_array_equal(np.array([1.0, 2.0, 3.0, 4.0]), model_values)
        assert_array_equal(np.array([True, False, True, False]), model_values.mask)

        assert_array_equal(np.array([1.1, 2.2, 2.9, 3.7]), ref_values)
        assert_array_equal(np.array([True, False, True, False]), ref_values.mask)
