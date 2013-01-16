from unittest import TestCase
from opec.Matchup import Matchup
from opec.MatchupEngine import ReferenceRecord

class MatchupTest(TestCase):

    def test_string(self):
        cell_position = [0, 0, 0, 0]
        spacetime_position = [300000, 0.12, 89.99, 179.99]
        rr = ReferenceRecord(0, 88.12, 178.24, 300100, 0.13)
        m = Matchup(cell_position, spacetime_position, rr)
        self.assertEqual('cell_position: [0, 0, 0, 0], spacetime_position: [300000, 0.12, 89.99, 179.99], reference_record: lat: 88.12, lon: 178.24, depth: 0.13, record_number: 0, time: 300100',
            m.__str__())
