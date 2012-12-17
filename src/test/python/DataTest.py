import unittest
from numpy import array
from numpy.testing import assert_array_equal
from src.main.python.Data import Data

class DataStorageTest(unittest.TestCase):

    def setUp(self):
        self.data = Data('../resources/test.nc')

    def test_model_vars(self):
        model_vars = self.data.model_vars()
        assert_array_equal(array(['chl', 'sst']), model_vars)

    def test_ref_vars(self):
        ref_vars = self.data.ref_vars()
        assert_array_equal(array(['chl_ref']), ref_vars)

#    def test_var_access(self):
#        pass

    def tearDown(self):
        self.data.close()
