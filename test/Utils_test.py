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

    def test_align_3dim_model_2dim_ref(self):
        ref_values = np.array([[0, 1], [2, 3]])
        model_values = np.array([[[0, 1], [2, 3]], [[4, 5], [6, 7]]])

        ref_values_aligned, model_values_aligned = Utils.align(ref_values, model_values)

        self.assertEqual(ref_values_aligned.shape, model_values_aligned.shape)

        assert_array_equal(np.array([[[0, 1], [2, 3]], [[0, 1], [2, 3]]]), ref_values_aligned)
        assert_array_equal(model_values, model_values_aligned)


    def test_align_4dim_model_2dim_ref(self):
        ref_values = np.arange(4).reshape((2, 2))
        model_values = np.arange(16).reshape((2, 2, 2, 2))

        ref_values_aligned, model_values_aligned = Utils.align(ref_values, model_values)

        self.assertEqual(ref_values_aligned.shape, model_values_aligned.shape)

        assert_array_equal(np.array([[[[0, 1], [2, 3]], [[0, 1], [2, 3]]], [[[0, 1], [2, 3]], [[0, 1], [2, 3]]]]), ref_values_aligned)
        assert_array_equal(model_values, model_values_aligned)


    def test_align_5dim_model_2dim_ref(self):
        ref_values = np.arange(4).reshape((2, 2))
        model_values = np.arange(32).reshape((2, 2, 2, 2, 2))

        ref_values_aligned, model_values_aligned = Utils.align(ref_values, model_values)

        self.assertEqual(ref_values_aligned.shape, model_values_aligned.shape)

        assert_array_equal(np.array([[[[[0, 1], [2, 3]], [[0, 1], [2, 3]]], [[[0, 1], [2, 3]], [[0, 1], [2, 3]]]],
                                     [[[[0, 1], [2, 3]], [[0, 1], [2, 3]]], [[[0, 1], [2, 3]], [[0, 1], [2, 3]]]]]), ref_values_aligned)
        assert_array_equal(model_values, model_values_aligned)


    def test_align_3dim_model_4dim_ref(self):
        ref_values = np.arange(16).reshape((2, 2, 2, 2))
        model_values = np.arange(8).reshape((2, 2, 2))

        ref_values_aligned, model_values_aligned = Utils.align(ref_values, model_values)

        self.assertEqual(ref_values_aligned.shape, model_values_aligned.shape)

        assert_array_equal(ref_values, ref_values_aligned)
        assert_array_equal([[[[0, 1], [2, 3]], [[4, 5], [6, 7]]], [[[0, 1], [2, 3]], [[4, 5], [6, 7]]]], model_values_aligned)


    def test_align_3dim_model_3dim_ref(self):
        model_values = np.arange(8).reshape((2, 2, 2))
        ref_values = np.arange(8, 16).reshape((2, 2, 2))

        ref_values_aligned, model_values_aligned = Utils.align(ref_values, model_values)

        self.assertEqual(ref_values_aligned.shape, model_values_aligned.shape)

        assert_array_equal(ref_values, ref_values_aligned)
        assert_array_equal(model_values, model_values_aligned)


    def test_align_2dim_model_1dim_ref(self):
        model_values = np.arange(6).reshape((3, 2))
        ref_values = np.arange(2)

        ref_values_aligned, model_values_aligned = Utils.align(ref_values, model_values)

        self.assertEqual(ref_values_aligned.shape, model_values_aligned.shape)

        assert_array_equal([[0, 1], [0, 1], [0, 1]], ref_values_aligned)
        assert_array_equal(model_values, model_values_aligned)

    def test_align_4dim_model_2dim_ref_2(self):
        model_values = np.arange(6).reshape((1, 3, 1, 2))
        ref_values = np.arange(2).reshape((1, 2))

        ref_values_aligned, model_values_aligned = Utils.align(ref_values, model_values)

        self.assertEqual(ref_values_aligned.shape, model_values_aligned.shape)

        assert_array_equal([[[[0, 1]], [[0, 1]], [[0, 1]]]], ref_values_aligned)
        assert_array_equal(model_values, model_values_aligned)

    def test_align_fails(self):
        model_values = np.arange(12).reshape((2, 3, 2))
        ref_values = np.arange(10).reshape((5, 2))

        try:
            Utils.align(model_values, ref_values)
            self.fail()
        except ValueError as e:
            self.assertEqual('Arrays are not alignable.', e.args[0])
