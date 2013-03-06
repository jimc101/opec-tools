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

import numpy as np
import numpy.ma as ma
import numpy.testing as test
from opec import Utils
from opec.Matchup import Matchup
from opec.ReferenceRecordsFinder import ReferenceRecord
from opec.Utils import harmonise

class Utils_test(unittest.TestCase):

    def test_extract_values(self):
        matchups = [
            Matchup([0, 0, 0, 0], [1261440000, 0.001, 55.2, 5.3], ReferenceRecord(0, 55.21, 5.31, 1261440250, 0.0012)),
            Matchup([0, 0, 0, 1], [1261440000, 0.001, 55.2, 5.8], ReferenceRecord(1, 55.8, 5.72, 1261440300, 0.0013))
        ]

        class DataMock(object):
            def get_reference_dimensions(self, ignored):
                return "recordNum"

            def read_reference(self, ignored_1, ignored_2):
                if hasattr(self, 'second_time_ref'):
                    return 0.2
                else:
                    self.second_time_ref = True
                    return np.nan

            def read_model(self, ignored_1, ignored_2):
                if hasattr(self, 'second_time_mod'):
                    return 0.2111
                else:
                    self.second_time_mod = True
                    return 0.1111

        ref, model = Utils.extract_values(matchups, DataMock(), 'chl_ref', 'chl')
        test.assert_almost_equal(ref, np.ma.array([np.nan, 0.2], mask=[True, False]))
        test.assert_almost_equal(model, np.ma.array([0.1111, 0.2111], mask=[False, False]))

    def test_harmonise_1(self):
        model_values = ma.array(np.arange(1.0, 5.0, 1), mask=np.array([False, False, True, False])) # [1, --, 3, 4]
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        ref_values, model_values = harmonise(ref_values, model_values)

        # Note: assert_array_equals does not tests if masks are equal
        # and there is no dedicated method for this
        # so masks need to be tested separately

        test.assert_array_equal(np.array([1, 2, 3, 4]), model_values)
        test.assert_array_equal(np.array([False, False, True, False]), model_values.mask)

        test.assert_array_equal(np.array([1.1, 2.2, 2.9, 3.7]), ref_values)
        test.assert_array_equal(np.array([False, False, True, False]), ref_values.mask)

    def test_harmonise_2(self):
        model_values = np.array(np.arange(1.0, 5.0, 1)) # [1, 2, 3, 4]
        ref_values = ma.array(np.array([1.1, 2.2, 2.9, 3.7]), mask=np.array([True, False, False, False]))
        ref_values, model_values = harmonise(ref_values, model_values)

        # Note: assert_array_equals does not tests if masks are equal
        # and there is no dedicated method for this
        # so masks need to be tested separately

        test.assert_array_equal(np.array([1, 2, 3, 4]), model_values)
        test.assert_array_equal(np.array([True, False, False, False]), model_values.mask)
        test.assert_array_equal(np.array([1.1, 2.2, 2.9, 3.7]), ref_values)
        test.assert_array_equal(np.array([True, False, False, False]), ref_values.mask)

    def test_harmonise_3(self):
        model_values = ma.array(np.arange(1.0, 5.0, 1), mask=np.array([False, False, True, False])) # [1, 2, --, 4]
        ref_values = ma.array([1.1, 2.2, 2.9, 3.7], mask=np.array([True, False, False, False]))
        ref_values, model_values = harmonise(ref_values, model_values)

        # Note: assert_array_equals does not tests if masks are equal
        # and there is no dedicated method for this
        # so masks need to be tested separately

        test.assert_array_equal(np.array([1.0, 2.0, 3.0, 4.0]), model_values)
        test.assert_array_equal(np.array([True, False, True, False]), model_values.mask)

        test.assert_array_equal(np.array([1.1, 2.2, 2.9, 3.7]), ref_values)
        test.assert_array_equal(np.array([True, False, True, False]), ref_values.mask)