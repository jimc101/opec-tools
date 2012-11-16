import unittest
from numpy import array
from numpy.testing import assert_array_equal
from src.main.python.UserFriendlyInteractiveDataStorage import UserFriendlyInteractiveDataStorage

class UserFriendlyInteractiveDataStorageTest(unittest.TestCase):

    def setUp(self):
        self.userFriendlyInteractiveDataStorage = UserFriendlyInteractiveDataStorage(inputFile='../resources/test.nc')

    def test_list_model_vars(self):
        printStream = MyPrintStream()
        self.userFriendlyInteractiveDataStorage.list_model_vars(printStream)
        assert_array_equal(array(['sst', 'chl']), printStream.printedValue)

    def test_list_model_vars_to_stdout(self):
        self.userFriendlyInteractiveDataStorage.list_model_vars()

    def test_list_ref_vars(self):
        printStream = MyPrintStream()
        self.userFriendlyInteractiveDataStorage.list_ref_vars(printStream)
        assert_array_equal(array(['sst', 'chl']), printStream.printedValue)

#    def test_var_access(self):
#        pass

    def tearDown(self):
        self.userFriendlyInteractiveDataStorage.close()

class MyPrintStream(object):

    def write(self, value):
        self.printedValue = value
        print self.printedValue