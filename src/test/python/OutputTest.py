from datetime import datetime
from unittest import TestCase
from src.main.python import Processor
from src.main.python.Data import Data
from src.main.python.MatchupEngine import MatchupEngine
from src.main.python.Output import Output, StringOutputter

class OutputTest(TestCase):

    def setUp(self):
        self.output = Output()

    def test_output_basic_statistics_from_dictionary(self):
        data = Data('../resources/test.nc')
        me = MatchupEngine(data)
        matchups = me.find_all_matchups('chl_ref', 'chl', 3)
        stats = Processor.compute_basic_statistics(matchups)

        so = StringOutputter()

        self.output.output_basic_statistics(stats, None, so, True, 3, '\t')

        now = datetime.now()
        self.assertEqual("##############################################################", so.strings[0])
        self.assertEqual("#", so.strings[1])
        self.assertEqual("# Benchmarking results", so.strings[2])
        self.assertEqual("#", so.strings[3])
        self.assertEqual("##############################################################", so.strings[4])
        self.assertEqual("#", so.strings[5])
        self.assertEqual("# Created on {} {}, {} at {}:{}:{}".format(now.month, now.day, now.year, now.hour, now.minute, now.second), so.strings[6])
        self.assertEqual("#", so.strings[7])
        self.assertEqual("# Matchup criteria:", so.strings[8])
        self.assertEqual("#    Macro pixel size = ", so.strings[9])
        self.assertEqual("#    Maximum geographic delta = 10 \"degrees\"", so.strings[10])
        self.assertEqual("#    Maximum time delta = 20000 seconds", so.strings[11])
        self.assertEqual("#    Maximum depth delta = 10 meters", so.strings[12])
        self.assertEqual("#", so.strings[13])
        self.assertEqual("# Number of matchups: {}".format(len(matchups)), so.strings[14])
