import unittest
import sys

class ApiTest(unittest.TestCase):

    def testThatOrderStaysUntouched(self):
        a = Sortable(2), Sortable(1)
        self.assertEqual(a[0].num, 2)
        self.assertEqual(a[1].num, 1)

    def testSortingUsingKey(self):
        a = Sortable(2), Sortable(1)
        sortedA = sorted(a, key = Sortable.getNumber)
        self.assertEqual(sortedA[0].num, 1)
        self.assertEqual(sortedA[1].num, 2)

    def testSortingUsingLambdaExpression(self):
        a = Sortable(2), Sortable(1)
        sortedA = sorted(a, key = lambda sortable: sortable.num)
        self.assertEqual(sortedA[0].num, 1)
        self.assertEqual(sortedA[1].num, 2)

class Sortable:

    def __init__(self, num):
        self.num = num

    def getNumber(self):
        return self.num