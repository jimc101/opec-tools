from unittest import TestCase
from opec.Matchup import Matchup

class MatchupTest(TestCase):

    def test_string(self):
        m = Matchup('bluh', 'blah', 10, 20, 1, 2, 3, 4, 5, 6, 7, 8)
        print(m.__str__())
        self.assertEqual('ref_variable_name: bluh, model_variable_name: blah, lat_delta: 4, ref_time: 3, ref_value: 10, depth_delta: 8, model_value: 20, ref_lon: 2, lon_delta: 5, ref_lat: 1, time_delta: 6, ref_depth: 7',
            m.__str__())
