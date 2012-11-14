import ogr
import unittest

class GDALTest(unittest.TestCase):

    def testReadSHP(self):
        driver = ogr.GetDriverByName('netCDF')
        dataset = driver.Open("resources/test.nc", 0)
        if dataset is None:
            self.fail("Couldn't open file")
