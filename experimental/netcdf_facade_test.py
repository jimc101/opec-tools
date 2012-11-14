import unittest
from numpy.core.numeric import array
from numpy.testing.utils import assert_array_equal
from experimental.netcdf_facade import NetCDFFacade

class NetCDFFacadeTest(unittest.TestCase):

    def setUp(self):
        filename = 'resources\\test.nc'
        self.netcdf = NetCDFFacade(filename)

    def tearDown(self):
        self.netcdf.close()

    def testGetDimSize(self):
        self.assertEqual(2, self.netcdf.getDimSize("time"))
        self.assertEqual(2, self.netcdf.getDimSize("depth"))
        self.assertEqual(2, self.netcdf.getDimSize("lat"))
        self.assertEqual(4, self.netcdf.getDimSize("lon"))

    def testGetGlobalAttributeValue(self):
        self.assertEqual("Some title", self.netcdf.getGlobalAttribute("title"))
        self.assertEqual("Some institution", self.netcdf.getGlobalAttribute("institution"))
        self.assertEqual("some link", self.netcdf.getGlobalAttribute("references"))
        self.assertEqual("my_chl_model", self.netcdf.getGlobalAttribute("source"))
        self.assertEqual("CF-1.6", self.netcdf.getGlobalAttribute("Conventions"))
        self.assertEqual("new_file", self.netcdf.getGlobalAttribute("history"))
        self.assertEqual("no_comment", self.netcdf.getGlobalAttribute("comment"))

    def testGetVariableAttribute(self):
        self.assertEqual("longitude", self.netcdf.getVariableAttribute("lon", "long_name"))
        self.assertAlmostEqual(-180.0, self.netcdf.getVariableAttribute("lon", "valid_min"), 5)

    def testGetDimensionString(self):
        self.assertEqual("lon", self.netcdf.getDimensionString("lon"))
        self.assertEqual("lat", self.netcdf.getDimensionString("lat"))
        self.assertEqual("time", self.netcdf.getDimensionString("time"))
        self.assertEqual("time depth lat lon", self.netcdf.getDimensionString("chl"))

    def testGetDimLength(self):
        self.assertEqual(2, self.netcdf.getDimLength("chl", 0))
        self.assertEqual(2, self.netcdf.getDimLength("chl", 1))
        self.assertEqual(2, self.netcdf.getDimLength("chl", 2))
        self.assertEqual(4, self.netcdf.getDimLength("chl", 3))

    def testGetDataViaOriginAndShape(self):
        assert_array_equal(array([0.1111], dtype='float32'),
            self.netcdf.getData("chl", [0, 0, 0, 0], [1, 1, 1, 1]))

        assert_array_equal(array([
            [
              [[ 0.1111, 0.2111], [ 0.1121, 0.2121]],
              [[ 0.1112, 0.2112], [ 0.1122, 0.2122]]
            ],
            [
              [[ 0.1113, 0.2113], [ 0.1123, 0.2123]],
              [[ 0.1114, 0.2114], [ 0.1124, 0.2124]]
            ]
        ],
            dtype='float32'), self.netcdf.getData("chl", [0, 0, 0, 0], [2, 2, 2, 2]))

    def testGetDimensions(self):
        assert_array_equal(["time", "depth", "lat", "lon", "record_num"], self.netcdf.getDimensions())