import unittest
import numpy as np
from numpy.testing import assert_array_equal
from src.main.python.Data import Data

class DataTest(unittest.TestCase):

    def setUp(self):
        self.data = Data('../resources/test.nc')

    def test_model_vars(self):
        model_vars = self.data.model_vars()
        assert_array_equal(np.array(['chl', 'sst']), model_vars)

    def test_ref_vars(self):
        ref_vars = self.data.ref_vars()
        assert_array_equal(np.array(['chl_ref']), ref_vars)

    def test_reference_records_count(self):
        self.assertEqual(3, self.data.reference_records_count())
        self.data = Data('../resources/test_without_records.nc')
        self.assertEqual(0, self.data.reference_records_count())

    def tearDown(self):
        self.data.close()

    def test_var_access(self):
        chl_variable = self.data.variable('chl', [0, 0, 0, 0], [1, 1, 1, 1])
        self.assertEqual(np.ndarray, type(chl_variable))
        self.assertEqual(1, chl_variable.size)
        self.assertAlmostEqual(0.1111, chl_variable[0])

        chl_variable = self.data.variable('chl')
        self.assertEqual(np.ndarray, type(chl_variable))
        self.assertEqual(32, chl_variable.size)
