# Copyright (C) 2013 Brockmann Consult GmbH (info@brockmann-consult.de)
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, see http://www.gnu.org/licenses/gpl.html

import unittest
from opec import Utils
import numpy as np
from numpy.testing import assert_array_equal


class Utils_test(unittest.TestCase):

    def test_get_indices_3dim_model_2dim_ref(self):
        ref_values = np.array([[0, 1], [2, 3]])
        model_values = np.array([[[0, 1], [2, 3]], [[4, 5], [6, 7]]])
        ref_indices, model_indices = Utils.align(ref_values, model_values)
        self.assertEqual(2, len(model_indices))

        self.assertIsNone(ref_indices)
        self.assertTupleEqual((0, ), model_indices[0])
        self.assertTupleEqual((1, ), model_indices[1])


        assert_array_equal(np.array([0, 1, 2, 3]).reshape((2, 2)), ref_values[:])
        assert_array_equal(np.array([0, 1, 2, 3]).reshape((2, 2)), model_values[model_indices[0]])
        assert_array_equal(np.array([4, 5, 6, 7]).reshape((2, 2)), model_values[model_indices[1]])


    def test_get_indices_4dim_model_2dim_ref(self):
        ref_values = np.arange(4).reshape((2, 2))
        model_values = np.arange(16).reshape((2, 2, 2, 2))
        ref_indices, model_indices = Utils.align(ref_values, model_values)

        self.assertEqual(4, len(model_indices))

        self.assertIsNone(ref_indices)
        self.assertTupleEqual((0, 0), model_indices[0])
        self.assertTupleEqual((0, 1), model_indices[1])
        self.assertTupleEqual((1, 0), model_indices[2])
        self.assertTupleEqual((1, 1), model_indices[3])

        assert_array_equal(np.array([0, 1, 2, 3]).reshape((2, 2)), ref_values[:])
        assert_array_equal(np.array([0, 1, 2, 3]).reshape((2, 2)), model_values[model_indices[0]])
        assert_array_equal(np.array([4, 5, 6, 7]).reshape((2, 2)), model_values[model_indices[1]])
        assert_array_equal(np.array([8, 9, 10, 11]).reshape((2, 2)), model_values[model_indices[2]])
        assert_array_equal(np.array([12, 13, 14, 15]).reshape((2, 2)), model_values[model_indices[3]])


    def test_get_indices_5dim_model_2dim_ref(self):
        ref_values = np.arange(4).reshape((2, 2))
        model_values = np.arange(32).reshape((2, 2, 2, 2, 2))
        ref_indices, model_indices = Utils.align(ref_values, model_values)

        self.assertEqual(8, len(model_indices))

        self.assertIsNone(ref_indices)
        self.assertTupleEqual((0, 0, 0), model_indices[0])
        self.assertTupleEqual((0, 0, 1), model_indices[1])
        self.assertTupleEqual((0, 1, 0), model_indices[2])
        self.assertTupleEqual((0, 1, 1), model_indices[3])
        self.assertTupleEqual((1, 0, 0), model_indices[4])
        self.assertTupleEqual((1, 0, 1), model_indices[5])
        self.assertTupleEqual((1, 1, 0), model_indices[6])
        self.assertTupleEqual((1, 1, 1), model_indices[7])


    def test_get_indices_3dim_model_4dim_ref(self):
        ref_values = np.arange(16).reshape((2, 2, 2, 2))
        model_values = np.arange(8).reshape((2, 2, 2))
        ref_indices, model_indices = Utils.align(ref_values, model_values)

        self.assertEqual(2, len(ref_indices))

        self.assertTupleEqual((0, ), ref_indices[0])
        self.assertTupleEqual((1, ), ref_indices[1])
        self.assertIsNone(model_indices)

        assert_array_equal(np.arange(8).reshape((2, 2, 2)), ref_values[ref_indices[0]])
        assert_array_equal(np.arange(8, 16).reshape((2, 2, 2)), ref_values[ref_indices[1]])
        assert_array_equal(np.arange(8).reshape((2, 2, 2)), model_values[:])


    def test_get_indices_3dim_model_3dim_ref(self):
        model_values = np.arange(8).reshape((2, 2, 2))
        ref_values = np.arange(8, 16).reshape((2, 2, 2))

        ref_indices, model_indices = Utils.align(ref_values, model_values)

        self.assertIsNone(ref_indices)
        self.assertIsNone(model_indices)
