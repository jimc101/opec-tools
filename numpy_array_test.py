import unittest
from numpy import *
import numpy
from numpy.testing.utils import assert_array_equal

class NumpyArrayTest(unittest.TestCase):

    def testBasicsForSimpleArrays(self):
        oneDimensionalTestArray = array([2, 3, 4])
        self.assertEqual(1, oneDimensionalTestArray.ndim)
        self.assertEqual((3,), oneDimensionalTestArray.shape)
        self.assertEqual(3, oneDimensionalTestArray.size)
        self.assertEqual(numpy.int, oneDimensionalTestArray.dtype)
        
        twoDimensionalTestArray = array([[2, 3, 4], [5.0, 6.0, 7.0]])
        self.assertEqual(2, twoDimensionalTestArray.ndim)
        self.assertEqual((2, 3,), twoDimensionalTestArray.shape)
        self.assertEqual(6, twoDimensionalTestArray.size)
        self.assertEqual(numpy.float, twoDimensionalTestArray.dtype)

        self.assertEqual(3.0, twoDimensionalTestArray[0, 1])

    def testArrayOperations(self):
        a = array([[2, 3, 4], [1, 2, 3]])
        a **= 2
        assert_array_equal(array([[4, 9, 16], [1, 4, 9]]), a)
        self.assertEqual(43, a.sum())
        a = a < 9
        assert_array_equal(array([[True, False, False], [True, True, False]]), a)

    def testOneDimensionalArrayIndexing(self):
        a = array([0, 1, 8, 27, 64, 125, 216, 343, 512, 729])
        self.assertEqual(0, a[0])
        self.assertEqual(729, a[9])
        assert_array_equal(array([1, 8, 27]), a[1:4:1])
        assert_array_equal(array([0, 8, 64]), a[0:5:2])

    def testTwoDimensionalArrayIndexing(self):
        a = array(
            [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [101, 102, 103, 104, 105, 106, 107, 108, 109, 110]]
        )
        self.assertEqual(2, a[(0, 1)])
        self.assertEqual(106, a[(1, 5)])

        firstRow = a[0, :]
        secondRow = a[1, :]

        assert_array_equal(array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), firstRow)
        assert_array_equal(array([101, 102, 103, 104, 105, 106, 107, 108, 109, 110]), secondRow)

        assert_array_equal(array([[5, 6, 7], [105, 106, 107]]), a[ : , 4:7:1])

    def testThreeDimensionalArrayIndexing(self):
        # create an array with len(dim0) = 1, len(dim1)=3, len(dim2)=4
        chl = array([
            [[1, 2, 3, 4], [4, 5, 6, 7], [8, 9, 10, 11]],
            [[11, 12, 13, 14], [14, 15, 16, 17], [18, 19, 110, 111]]
        ])

        self.assertEqual(4, chl[0, 0, 3])
        # let's say dim0 = time, dim1 = lat, dim2 = lon
        # then get values for each point in time at second lat and third lon point
        # --> 1-dim array
        assert_array_equal(array([6, 16]), chl[:,1,2])

        # now get values for each point in time at the second lat and all lon points
        # --> 2-dim array
        # dim0 = time, dim1 = lon
        assert_array_equal(array([
            [4, 5, 6, 7], [14, 15, 16, 17]
        ]), chl[:,1,:])

        # now get values for the first point in time at all lat and all lon points
        # --> 2-dim array
        # dim0 = lat, dim1 = lon
        assert_array_equal(array([
            [1, 2, 3, 4], [4, 5, 6, 7], [8, 9, 10, 11],
        ]), chl[0,:,:])

        # now get values for the each point in time at some lat and some lon points
        # --> 3-dim array
        # dim0 = time, dim1 = lat, dim2 = lon
        assert_array_equal(array([
            [[4, 5], [8, 9]],
            [[14, 15], [18, 19]]
        ]), chl[:, 1:3, 0:2])

