from datetime import datetime
from unittest import TestCase
from opec import Processor
from opec.Matchup import Matchup
from opec.MatchupEngine import ReferenceRecord
from opec.Output import Output
from opec.Configuration import Configuration
import os.path as path
import os as os

class OutputTest(TestCase):

    @classmethod
    def setUpClass(self):
        self.cwd = os.getcwd()
        os.chdir('..')

    @classmethod
    def tearDownClass(self):
        os.chdir(self.cwd)

    def setUp(self):
        self.config = Configuration(1, 1, 0, 123, 12, 1234, 0.234)
        self.stats = Processor.calculate_statistics(reference_values=[10, 10, 10, 10], model_values=[11, 9, 11.2, 10.5], config=self.config)
        self.temp_filename = 'resources/test_output.csv'

    def tearDown(self):
        if path.exists(self.temp_filename):
            os.remove(self.temp_filename)
            if path.exists(self.temp_filename):
                self.fail('Failed to delete {}'.format(self.temp_filename))

    def test_output_csv(self):
        output = Output(config=self.config)
        expected_result = []
        expected_result.append("##############################################################")
        expected_result.append("#")
        expected_result.append("# Benchmarking results")
        expected_result.append("#")
        expected_result.append("##############################################################")
        expected_result.append("#")
        expected_result.append("# Performed at {}".format(datetime.now().strftime('%b %d, %Y at %H:%M:%S')))
        expected_result.append("#")
        expected_result.append("# Number of matchups: 1")
        expected_result.append("#")
        expected_result.append("# Matchup criteria:")
        expected_result.append("#    Maximum geographic delta = 12.0 \"degrees\"")
        expected_result.append("#    Maximum time delta = 1234 seconds")
        expected_result.append("#    Maximum depth delta = 0.234 meters")
        expected_result.append("#")
        expected_result.append("# Algorithm parameters:")
        expected_result.append("#    ddof (delta degrees of freedom, used for computation of stddev) = 0")
        expected_result.append("#    alpha (used for percentile computation) = 1")
        expected_result.append("#    beta (used for percentile computation) = 1")
        expected_result.append("#")
        expected_result.append("# Statistics for variable 'chl' with reference 'chl_ref':")
        expected_result.append("")
        expected_result.append("rmse\t0.9605")
        expected_result.append("unbiased_rmse\t0.8613")
        expected_result.append("bias\t-0.425")
        expected_result.append("pbias\t-4.25")
        expected_result.append("corrcoeff\tnan")
        expected_result.append("reliability_index\t1.0417")
        expected_result.append("model_efficiency\tnan")
        expected_result.append("")
        expected_result.append("# Statistics of variable 'chl':")
        expected_result.append("")
        expected_result.append("min\t9")
        expected_result.append("max\t11.2")
        expected_result.append("mean\t10.425")
        expected_result.append("stddev\t0.8613")
        expected_result.append("median\t10.75")
        expected_result.append("p90\t11.14")
        expected_result.append("p95\t11.17")
        expected_result.append("")
        expected_result.append("# Statistics of variable 'chl_ref':")
        expected_result.append("")
        expected_result.append("min\t10")
        expected_result.append("max\t10")
        expected_result.append("mean\t10")
        expected_result.append("stddev\t0")
        expected_result.append("median\t10")
        expected_result.append("p90\t10")
        expected_result.append("p95\t10")
        expected_result.append("")
        expected_result.append("# Matchups:")
        expected_result.append("")
        expected_result.append("# Matchup 1:")
        expected_result.append("")
        expected_result.append("reference_time:\t300200")
        expected_result.append("reference_depth:\t0.11")
        expected_result.append("reference_lat:\t5.4")
        expected_result.append("reference_lon:\t55.3")
        expected_result.append("model_time:\t300000")
        expected_result.append("model_depth:\t0.12")
        expected_result.append("model_lat:\t55.1")
        expected_result.append("model_lon:\t5.3")

        matchups = [Matchup([0, 0, 0, 0], [300000, 0.12, 55.1, 5.3], ReferenceRecord(0, 5.4, 55.3, 300200, 0.11))]
        self.assertTrue(output.csv(self.stats, 'chl', 'chl_ref', matchups=matchups).startswith("\n".join(expected_result)))

    def test_write_csv_file(self):
        output = Output()
        self.assertFalse(path.exists(self.temp_filename))
        output.csv(self.stats, 'Heidi', 'some_ref', target_file=self.temp_filename)
        self.assertTrue(path.exists(self.temp_filename))
        os.remove(self.temp_filename)
        self.assertFalse(path.exists(self.temp_filename))

    def test_output_xhtml(self):
        output = Output()
        matchup_1 = Matchup([0, 0, 0, 0], [300000, 0.12, 55.1, 5.3], ReferenceRecord(0, 5.4, 55.3, 300200, 0.11))
        matchup_2 = Matchup([0, 0, 0, 1], [300000, 0.12, 55.1, 5.3], ReferenceRecord(1, 5.8, 57.2, 300400, 0.12))
        matchups = [matchup_1, matchup_2]
        self.xml_target_file = 'resources/matchup_report.xml'
        output.xhtml(self.stats, matchups, self.xml_target_file)
#        os.remove(self.xml_target_file)