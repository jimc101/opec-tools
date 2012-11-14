import os
import unittest
from experimental.csv_export import CsvExporter

class CsvExportTest(unittest.TestCase):

    def setUp(self):
        self.csvExporter = CsvExporter("resources\\filename.csv")

    def testCsvExport(self):
        self.csvExporter.initialize(["rmse", "bias", "unbiased_rmse", "corrCoeff"])

        statistics_1 = dict(rmse=0.5, bias=-2.0, unbiased_rmse=1.0, corrCoeff=0.35)
        statistics_2 = dict(rmse=0.7, bias=-2.1, unbiased_rmse=1.2, corrCoeff=0.45)
        self.csvExporter.addData("chl", 55.2, 8.6, statistics_1)
        self.csvExporter.addData("chl", 55.1, 8.2, statistics_2)
        self.csvExporter.finalize()

        self.assertTrue(os.path.exists("resources\\filename.csv"))
        file = open("resources\\filename.csv")
        self.assertEquals("variable_name\tlat\tlon\tbias\tcorrCoeff\trmse\tunbiased_rmse\n", file.readline())
        self.assertEquals("chl\t55.2\t8.6\t-2.0\t0.35\t0.5\t1.0\n", file.readline())
        self.assertEquals("chl\t55.1\t8.2\t-2.1\t0.45\t0.7\t1.2\n", file.readline())

    def tearDown(self):
        try:
            os.remove("resources\\filename.csv")
        except OSError:
            pass
            # file does not exist. That's ok.