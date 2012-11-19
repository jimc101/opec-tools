import unittest
from numpy import array
from numpy.testing import assert_array_equal
from src.main.python.UserFriendlyInteractiveDataStorage import UserFriendlyInteractiveDataStorage

class UserFriendlyInteractiveDataStorageTest(unittest.TestCase):

    def setUp(self):
        self.userFriendlyInteractiveDataStorage = UserFriendlyInteractiveDataStorage(inputFile='../resources/test.nc')

    def test_list_model_vars(self):
        model_vars = self.userFriendlyInteractiveDataStorage.list_model_vars()
        assert_array_equal(array(['sst', 'chl']), model_vars)

    def test_list_ref_vars(self):
        ref_vars = self.userFriendlyInteractiveDataStorage.list_ref_vars()
        assert_array_equal(array(['chl_ref']), ref_vars)

#    def test_var_access(self):
#        pass

    def tearDown(self):
        self.userFriendlyInteractiveDataStorage.close()
