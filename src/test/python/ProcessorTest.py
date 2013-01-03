from unittest import TestCase
import numpy as np
import numpy.ma as ma
from numpy.testing import assert_array_equal
from src.main.python.Data import Data
from src.main.python.MatchupEngine import MatchupEngine
from src.main.python.Processor import compute_basic_statistics, harmonise

class ProcessorTest(TestCase):

    def setUp(self):
        self.data = Data('../resources/test.nc')
        self.me = MatchupEngine(self.data)

    def tearDown(self):
        self.data.close()

    def test_compute_basic_statistics_for_matchups(self):
        matchups = self.me.find_all_matchups('chl_ref', 'chl', 3)
        basic_statistics = compute_basic_statistics(matchups)
        self.assertIsNotNone(basic_statistics)
        self.assertEqual(7, len(basic_statistics))
        self.assertAlmostEqual(0.0960456, basic_statistics['rmsd'], 5)
        self.assertAlmostEqual(0.0868041, basic_statistics['unbiased_rmsd'], 5)
        self.assertAlmostEqual(20.553573, basic_statistics['pbias'], 5)
        self.assertAlmostEqual(0.0411071, basic_statistics['bias'], 5)
        self.assertAlmostEqual(0.077279, basic_statistics['corrcoeff'], 5)
        self.assertAlmostEqual(1.2662666, basic_statistics['reliability_index'], 5)
        self.assertAlmostEqual(-0.6143319, basic_statistics['model_efficiency'], 5)

        self.assertAlmostEqual(basic_statistics['rmsd'] ** 2, basic_statistics['bias'] ** 2 + basic_statistics['unbiased_rmsd'] ** 2, 5)

    def test_compute_basic_statistics(self):
        model_values = np.array(range(1, 5, 1)) # [1, 2, 3, 4]
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        basic_statistics = compute_basic_statistics(reference_values=ref_values, model_values=model_values)
        self.assertIsNotNone(basic_statistics)
        self.assertEqual(7, len(basic_statistics))
        self.assertAlmostEqual(0.192028, basic_statistics['unbiased_rmsd'], 5)
        self.assertAlmostEqual(0.193649, basic_statistics['rmsd'], 5)
        self.assertAlmostEqual(-1.0101, basic_statistics['pbias'], 5)
        self.assertAlmostEqual(-0.025, basic_statistics['bias'], 5)
        self.assertAlmostEqual(0.99519, basic_statistics['corrcoeff'], 5)
        self.assertAlmostEqual(1.03521, basic_statistics['reliability_index'], 5)
        self.assertAlmostEqual(0.9588759, basic_statistics['model_efficiency'], 5)

        self.assertAlmostEqual(basic_statistics['rmsd'] ** 2, basic_statistics['bias'] ** 2 + basic_statistics['unbiased_rmsd'] ** 2, 5)

    def test_compute_basic_statistics_with_masked_values(self):
        model_values = ma.array(np.arange(1.0, 5.0, 1), mask=np.array([False, False, True, False])) # [1, 2, --, 4]
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        basic_statistics = compute_basic_statistics(reference_values=ref_values, model_values=model_values)
        self.assertIsNotNone(basic_statistics)
        self.assertEqual(7, len(basic_statistics))
        self.assertAlmostEqual(0.216024, basic_statistics['unbiased_rmsd'], 5)
        self.assertAlmostEqual(0.216024, basic_statistics['rmsd'], 5)
        self.assertAlmostEqual(6.344131e-15, basic_statistics['pbias'], 5)
        self.assertAlmostEqual(0.0, basic_statistics['bias'], 5)
        self.assertAlmostEqual(0.99484975, basic_statistics['corrcoeff'], 5)
        self.assertAlmostEqual(1.039815, basic_statistics['reliability_index'], 5)
        self.assertAlmostEqual(0.9589041, basic_statistics['model_efficiency'], 5)

        self.assertAlmostEqual(basic_statistics['rmsd'] ** 2, basic_statistics['bias'] ** 2 + basic_statistics['unbiased_rmsd'] ** 2, 5)

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
