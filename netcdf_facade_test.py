import unittest
from numpy.core.numeric import array
from numpy.testing.utils import assert_array_equal
from netcdf_facade import NetCDFFacade

class NetCDFFacadeTest(unittest.TestCase):

    def setUp(self):
        filename = 'resources\\test.nc'
        self.netcdf = NetCDFFacade(filename)

    def tearDown(self):
        self.netcdf.close()

    def testGetDimSize(self):
        self.assertEqual(4, self.netcdf.getDimSize("latitude"))
        self.assertEqual(4, self.netcdf.getDimSize("longitude"))

    def testGetGlobalAttributeValue(self):
        self.assertEqual("COARDS", self.netcdf.getGlobalAttribute("Conventions"))
        self.assertEqual("test file", self.netcdf.getGlobalAttribute("history"))
        self.assertEqual("date=2006-02-13", self.netcdf.getGlobalAttribute("comment"))

    def testGetVariableAttribute(self):
        self.assertEqual("longitude", self.netcdf.getVariableAttribute("longitude", "long_name"))
        self.assertAlmostEqual(9.00885, self.netcdf.getVariableAttribute("longitude", "valid_min"), 5)

    def testGetDimensionString(self):
        self.assertEqual("longitude", self.netcdf.getDimensionString("longitude"))
        self.assertEqual("latitude", self.netcdf.getDimensionString("latitude"))
        self.assertEqual("time", self.netcdf.getDimensionString("time"))
        self.assertEqual("time latitude longitude", self.netcdf.getDimensionString("chlorophyll_concentration_in_sea_water"))

    def testGetDimLength(self):
        self.assertEqual(2, self.netcdf.getDimLength("chlorophyll_concentration_in_sea_water", 0))
        self.assertEqual(4, self.netcdf.getDimLength("chlorophyll_concentration_in_sea_water", 1))
        self.assertEqual(4, self.netcdf.getDimLength("chlorophyll_concentration_in_sea_water", 2))

    def testGetDataViaOriginAndShape(self):
        assert_array_equal(array([
            [[7, 8], [11, 12]],
            [[17, 18], [111, 112]]
        ]), self.netcdf.getData("chlorophyll_concentration_in_sea_water", [0, 1, 2], [2, 2, 2]))

        assert_array_equal(array([
            [[1, 2, 3, 4], [5, 6, 7, 8]]
        ]), self.netcdf.getData("chlorophyll_concentration_in_sea_water", [0, 0, 0], [1, 2, 4]))

        assert_array_equal(array([
            [[11, 12, 13, 14],
             [15, 16, 17, 18],
             [19, 110, 111, 112],
             [113, 114, 115, 116]]
        ]), self.netcdf.getData("chlorophyll_concentration_in_sea_water", [1, 0, 0], [1, 4, 4]))

    def testGetDataViaLatLonTime(self):
        assert_array_equal(array([
            [[110, 111],
             [114, 115]]
        ]), self.netcdf.getDataForLatLonTime("chlorophyll_concentration_in_sea_water", 20, 20, 55.7, 56, 9.3, 9.7))