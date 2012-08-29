import unittest
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
        self.assertEqual("latitude longitude", self.netcdf.getDimensionString("chlorophyll_concentration_in_sea_water"))

    def testGetSingleVariableValue(self):
        self.assertEqual(7, self.netcdf.getData("chlorophyll_concentration_in_sea_water", [1, 2], [1, 1]))
