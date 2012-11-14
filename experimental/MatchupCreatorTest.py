import unittest
from experimental import MatchupCreator

__author__ = 'Thomas Storm'

class MatchupCreatorTest(unittest.TestCase):

    def setUp(self):
        filename = 'resources\\test.nc'
        self.matchupCreator = MatchupCreator(filename)

    def tearDown(self):
        self.matchupCreator.close()

    def testInitialise(self):
        self.assertEqual(4, len(self.matchupCreator.coordinateVariables))
        timeCoordinateVariable = self.matchupCreator.coordinateVariables[0]
        self.assertEqual('time', timeCoordinateVariable.name)
        self.assertEqual(1261440000, timeCoordinateVariable.values[0])
        self.assertEqual(1261447200, timeCoordinateVariable.values[1])

    def testGetMatchups(self):
        matchups = self.matchupCreator.getMatchups()
        self.assertEqual(3, len(matchups))
        pass