from unittest import TestCase
import numpy as np
from src.main.python.Data import Data
from src.main.python.MatchupEngine import MatchupEngine
from src.main.python.Processor import compute_basic_statistics

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
        self.assertAlmostEqual(0.0986998, basic_statistics['rmsd'], 5)
        self.assertAlmostEqual(0.0923173, basic_statistics['unbiased_rmsd'], 5)
        self.assertAlmostEqual(17.458335, basic_statistics['pbias'], 5)
        self.assertAlmostEqual(0.0349167, basic_statistics['bias'], 5)
        self.assertAlmostEqual(0.0812849, basic_statistics['corrcoeff'], 5)
        self.assertAlmostEqual(1.2703836, basic_statistics['reliability_index'], 5)
        self.assertAlmostEqual(-0.461248, basic_statistics['model_efficiency'], 5)

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

    def test_compute_basic_statistics_with_nan(self):
        model_values = np.array(np.arange(1.0, 5.0, 1)) # [1, 2, 3, 4]
        model_values[2] = np.nan
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