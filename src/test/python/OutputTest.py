from datetime import datetime
from unittest import TestCase
from src.main.python import Processor
from src.main.python.Matchup import Matchup
from src.main.python.Output import Output, StringOutputter

class OutputTest(TestCase):

    def setUp(self):
        self.output = Output()

    def test_output_basic_statistics_from_dictionary(self):

        matchups = [
            Matchup('chl_ref', 'chl', 10, 11, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 9, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 11.2, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 10.5, 55, 20, 10000, 0, 0, 0, 0.1, 0)
        ]
        stats = Processor.basic_statistics(matchups)

        so = StringOutputter()

        self.output.output_basic_statistics('chl', 'chl_ref', 4, stats, so, True, 123, 12, 1234, 0.234, 'somethingsomethingsomethingdarkside', '\t')

        now = datetime.now()
        self.assertEqual("##############################################################", so.strings[0])
        self.assertEqual("#", so.strings[1])
        self.assertEqual("# Benchmarking results of file \'somethingsomethingsomethingdarkside\'", so.strings[2])
        self.assertEqual("#", so.strings[3])
        self.assertEqual("##############################################################", so.strings[4])
        self.assertEqual("#", so.strings[5])
        self.assertEqual("# Created on {} {}, {} at {}:{}:{}".format(now.month, now.day, now.year, now.hour, now.minute, now.second), so.strings[6])
        self.assertEqual("#", so.strings[7])
        self.assertEqual("# Matchup criteria:", so.strings[8])
        self.assertEqual("#    Macro pixel size = 123", so.strings[9])
        self.assertEqual("#    Maximum geographic delta = 12 \"degrees\"", so.strings[10])
        self.assertEqual("#    Maximum time delta = 1234 seconds", so.strings[11])
        self.assertEqual("#    Maximum depth delta = 0.234 meters", so.strings[12])
        self.assertEqual("#", so.strings[13])
        self.assertEqual("variable_name\tref_variable_name\tmatchup_count\tmin\tmax\tmean\tstddev\tmedian\tp90\tp95\tref_min\tref_max\tref_mean\tref_stddev\tref_median\tref_p90\tref_p95\trmsd\tunbiased_rmsd\tbias\tpbias\tcorrcoeff\treliability_index\tmodel_efficiency", so.strings[14])
        self.assertEqual("chl\tchl_ref\t4\t9.0\t11.2\t10.425\t0.861321658848\t10.75\t11.14\t11.17\t10.0\t10.0\t10.0\t0.0\t10.0\t10.0\t10.0\t0.960468635615\t0.861321658848\t-0.425\t-4.25\t--\t1.04170735296\tnan", so.strings[15])

    def test_output_basic_statistics_from_data(self):
        pass