import unittest
import numpy
from numpy.core.numeric import array
from numpy.testing.utils import assert_array_equal
from src.main.python.NetcdfFacade import NetCDFFacade

class NetCDFFacadeTest(unittest.TestCase):

    def setUp(self):
        filename = '../resources/test.nc'
        self.netcdf = NetCDFFacade(filename)

    def tearDown(self):
        self.netcdf.close()

    def testGetDimSize(self):
        self.assertEqual(2, self.netcdf.getDimSize("time"))
        self.assertEqual(2, self.netcdf.getDimSize("depth"))
        self.assertEqual(2, self.netcdf.getDimSize("lat"))
        self.assertEqual(4, self.netcdf.getDimSize("lon"))

    def testGetGlobalAttributeValue(self):
        self.assertEqual("some title", self.netcdf.getGlobalAttribute("title"))
        self.assertEqual("institution code", self.netcdf.getGlobalAttribute("institution"))
        self.assertEqual("links to references", self.netcdf.getGlobalAttribute("references"))
        self.assertEqual("method of production", self.netcdf.getGlobalAttribute("source"))
        self.assertEqual("CF-1.6", self.netcdf.getGlobalAttribute("Conventions"))
        self.assertEqual("audit trail", self.netcdf.getGlobalAttribute("history"))
        self.assertEqual("comment", self.netcdf.getGlobalAttribute("comment"))

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

    def testGetGeophysicalVariables(self):
        assert_array_equal(['chl', 'sst'], self.netcdf.getGeophysicalVariables())

    def testReadVariableFully(self):
        fullyReadChl = self.netcdf.readVariableFully('chl')
        assert_array_equal(
            array(
            [[[[0.1111, 0.2111, 0.1211, 0.2211],
               [0.1121, 0.2121, 0.1221, 0.2221]],
              [[0.1112, 0.2112, 0.1212, 0.2212],
               [0.1122, 0.2122, 0.1222, 0.2222]]],
             [[[0.1113, 0.2113, 0.1213, 0.2213],
               [0.1123, 0.2123, 0.1223, 0.2223]],
              [[0.1114, 0.2114, 0.1214, 0.2214],
               [0.1124, 0.2124, 0.1224, 0.2224]]]], dtype='float32'),
            fullyReadChl)

    def testGetVariableSize(self):
        self.assertEqual(2, self.netcdf.getVariableSize('lat'))
        self.assertEqual(4, self.netcdf.getVariableSize('lon'))
        self.assertEqual(2, self.netcdf.getVariableSize('time'))
        self.assertEqual(32, self.netcdf.getVariableSize('chl'))
        self.assertEqual(32, self.netcdf.getVariableSize('sst'))
        self.assertEqual(32, self.netcdf.getVariableSize('sst'))
        self.assertEqual(3, self.netcdf.getVariableSize('chl_ref'))