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

from unittest import TestCase
import numpy as np
import numpy.ma as ma
from numpy.testing import assert_almost_equal, assert_array_equal
from opec.Matchup import Matchup
from opec.Processor import calculate_statistics, harmonise, extract_values
from opec.Configuration import Configuration
from opec.MatchupEngine import MatchupEngine
from opec.Data import Data
import os
from opec.MatchupEngine import ReferenceRecord

class Processor_test(TestCase):

    def setUp(self):
        path = os.path.dirname(os.path.realpath(__file__)) + '/../'
        self.data = Data(path + 'resources/test.nc')
        self.config = Configuration(geo_delta=10, time_delta=86400, depth_delta=12, ddof=0, alpha=1, beta=1)
        self.me = MatchupEngine(self.data, self.config)

    def tearDown(self):
        self.data.close()

    def test_compute_statistics_for_matchups(self):
        matchups = self.me.find_all_matchups()
        stats = calculate_statistics(matchups, config=self.config, ref_name='chl_ref', model_name='chl', unit='megazork')
        self.assertEqual('chl', stats['model_name'])
        self.assertEqual('chl_ref', stats['ref_name'])
        self.assertEqual('megazork', stats['unit'])
        self.assertAlmostEqual(0.04570989, stats['rmse'], 5)
        self.assertAlmostEqual(0.04181358, stats['unbiased_rmse'], 5)
        self.assertAlmostEqual(0.512109, stats['normalised_rmse'], 5)
        self.assertAlmostEqual(9.2333366, stats['pbias'], 5)
        self.assertAlmostEqual(0.01846667, stats['bias'], 5)
        self.assertAlmostEqual(0.908450244, stats['corrcoeff'], 5)
        self.assertAlmostEqual(1.084043, stats['reliability_index'], 5)
        self.assertAlmostEqual(0.686590903, stats['model_efficiency'], 5)
        self.assertAlmostEqual(0.18153333, stats['mean'], 5)
        self.assertAlmostEqual(0.2, stats['ref_mean'], 5)
        self.assertAlmostEqual(0.050017, stats['stddev'], 5)
        self.assertAlmostEqual(0.0816496, stats['ref_stddev'], 5)
        self.assertAlmostEqual(0.211099, stats['median'], 5)
        self.assertAlmostEqual(0.2, stats['ref_median'], 5)
        self.assertAlmostEqual(0.220139, stats['p90'], 5)
        self.assertAlmostEqual(0.28, stats['ref_p90'], 5)
        self.assertAlmostEqual(0.22126999, stats['p95'], 5)
        self.assertAlmostEqual(0.29, stats['ref_p95'], 5)
        self.assertAlmostEqual(0.1111, stats['min'], 5)
        self.assertAlmostEqual(0.1, stats['ref_min'], 5)
        self.assertAlmostEqual(0.2224, stats['max'], 5)
        self.assertAlmostEqual(0.3, stats['ref_max'], 5)

        self.assertAlmostEqual(stats['rmse'] ** 2, stats['bias'] ** 2 + stats['unbiased_rmse'] ** 2, 5)

    def test_compute_statistics(self):
        model_values = np.array(range(1, 5, 1)) # [1, 2, 3, 4]
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        stats = calculate_statistics(reference_values=ref_values, model_values=model_values, config=self.config)
        self.assertIsNone(stats['model_name'])
        self.assertIsNone(stats['ref_name'])
        self.assertAlmostEqual(0.192028, stats['unbiased_rmse'], 5)
        self.assertAlmostEqual(0.193649, stats['rmse'], 5)
        self.assertAlmostEqual(0.2010936411, stats['normalised_rmse'], 5)
        self.assertAlmostEqual(-1.0101, stats['pbias'], 5)
        self.assertAlmostEqual(-0.025, stats['bias'], 5)
        self.assertAlmostEqual(0.99519, stats['corrcoeff'], 5)
        self.assertAlmostEqual(1.03521, stats['reliability_index'], 5)
        self.assertAlmostEqual(0.9588759, stats['model_efficiency'], 5)
        self.assertAlmostEqual(2.5, stats['mean'], 5)
        self.assertAlmostEqual(2.475, stats['ref_mean'], 5)
        self.assertAlmostEqual(1.11803, stats['stddev'], 5)
        self.assertAlmostEqual(0.954921, stats['ref_stddev'], 5)
        self.assertAlmostEqual(2.5, stats['median'], 5)
        self.assertAlmostEqual(2.55, stats['ref_median'], 5)
        self.assertAlmostEqual(3.7, stats['p90'], 5)
        self.assertAlmostEqual(3.46, stats['ref_p90'], 5)
        self.assertAlmostEqual(3.85, stats['p95'], 5)
        self.assertAlmostEqual(3.58, stats['ref_p95'], 5)
        self.assertAlmostEqual(1, stats['min'], 5)
        self.assertAlmostEqual(1.1, stats['ref_min'], 5)
        self.assertAlmostEqual(4, stats['max'], 5)
        self.assertAlmostEqual(3.7, stats['ref_max'], 5)

        self.assertAlmostEqual(stats['rmse'] ** 2, stats['bias'] ** 2 + stats['unbiased_rmse'] ** 2, 5)

    def test_compute_statistics_with_masked_values(self):
        model_values = ma.array(np.arange(1.0, 5.0, 1), mask=np.array([False, False, True, False])) # [1, 2, --, 4]
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        stats = calculate_statistics(reference_values=ref_values, model_values=model_values, config=self.config, model_name='kate', ref_name='ref')
        self.assertEqual('kate', stats['model_name'])
        self.assertEqual('ref', stats['ref_name'])
        self.assertAlmostEqual(0.216024, stats['unbiased_rmse'], 5)
        self.assertAlmostEqual(0.216024, stats['rmse'], 5)
        self.assertAlmostEqual(6.344131e-15, stats['pbias'], 5)
        self.assertAlmostEqual(0.0, stats['bias'], 5)
        self.assertAlmostEqual(0.99484975, stats['corrcoeff'], 5)
        self.assertAlmostEqual(1.039815, stats['reliability_index'], 5)
        self.assertAlmostEqual(0.9589041, stats['model_efficiency'], 5)
        self.assertAlmostEqual(2.3333333, stats['mean'], 5)
        self.assertAlmostEqual(2.3333333, stats['ref_mean'], 5)
        self.assertAlmostEqual(1.24722, stats['stddev'], 5)
        self.assertAlmostEqual(1.06562, stats['ref_stddev'], 5)
        self.assertAlmostEqual(2, stats['median'], 5)
        self.assertAlmostEqual(2.2, stats['ref_median'], 5)
        self.assertAlmostEqual(3.6, stats['p90'], 5)
        self.assertAlmostEqual(3.4, stats['ref_p90'], 5)
        self.assertAlmostEqual(3.8, stats['p95'], 5)
        self.assertAlmostEqual(3.55, stats['ref_p95'], 5)
        self.assertAlmostEqual(1, stats['min'], 5)
        self.assertAlmostEqual(1.1, stats['ref_min'], 5)
        self.assertAlmostEqual(4, stats['max'], 5)
        self.assertAlmostEqual(3.7, stats['ref_max'], 5)

        self.assertAlmostEqual(stats['rmse'] ** 2, stats['bias'] ** 2 + stats['unbiased_rmse'] ** 2, 5)

    def test_compute_statistics_with_extreme_model_values(self):
        model_values = np.array(range(1, 5, 1)) # [1, 2, 3, 4]
        ref_values = np.array([1, 1, 1, 1])
        stats = calculate_statistics(reference_values=ref_values, model_values=model_values, config=self.config)
        self.assertAlmostEqual(1.118034, stats['unbiased_rmse'], 5)
        self.assertAlmostEqual(1.870829, stats['rmse'], 5)
        self.assertAlmostEqual(-150, stats['pbias'], 5)
        self.assertAlmostEqual(-1.5, stats['bias'], 5)
        self.assertTrue(np.isnan(stats['corrcoeff']))
        self.assertAlmostEqual(1.5106421, stats['reliability_index'], 5)
        self.assertTrue(np.isnan(stats['model_efficiency']))
        self.assertAlmostEqual(2.5, stats['mean'], 5)
        self.assertAlmostEqual(1, stats['ref_mean'], 5)
        self.assertAlmostEqual(1.11803, stats['stddev'], 5)
        self.assertAlmostEqual(0.0, stats['ref_stddev'], 5)
        self.assertAlmostEqual(2.5, stats['median'], 5)
        self.assertAlmostEqual(1, stats['ref_median'], 5)
        self.assertAlmostEqual(3.7, stats['p90'], 5)
        self.assertAlmostEqual(1, stats['ref_p90'], 5)
        self.assertAlmostEqual(3.85, stats['p95'], 5)
        self.assertAlmostEqual(1, stats['ref_p95'], 5)
        self.assertAlmostEqual(1, stats['min'], 5)
        self.assertAlmostEqual(1, stats['ref_min'], 5)
        self.assertAlmostEqual(4, stats['max'], 5)
        self.assertAlmostEqual(1, stats['ref_max'], 5)

        self.assertAlmostEqual(stats['rmse'] ** 2, stats['bias'] ** 2 + stats['unbiased_rmse'] ** 2, 5)

    def test_compute_statistics_with_extreme_reference_values(self):
        model_values = np.array([1, 1, 1, 1])
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        stats = calculate_statistics(reference_values=ref_values, model_values=model_values, config=self.config)
        self.assertAlmostEqual(0.954921, stats['unbiased_rmse'], 5)
        self.assertAlmostEqual(1.757128, stats['rmse'], 5)
        self.assertAlmostEqual(59.595959, stats['pbias'], 5)
        self.assertAlmostEqual(1.475, stats['bias'], 5)
        self.assertTrue(np.isnan(stats['corrcoeff']))
        self.assertAlmostEqual(1.49908579, stats['reliability_index'], 5)
        self.assertAlmostEqual(-2.38588, stats['model_efficiency'], 5)
        self.assertAlmostEqual(1.0, stats['mean'], 5)
        self.assertAlmostEqual(2.475, stats['ref_mean'], 5)
        self.assertAlmostEqual(0, stats['stddev'], 5)
        self.assertAlmostEqual(0.954921, stats['ref_stddev'], 5)
        self.assertAlmostEqual(1, stats['median'], 5)
        self.assertAlmostEqual(2.545, stats['ref_median'], 2)
        self.assertAlmostEqual(1, stats['p90'], 5)
        self.assertAlmostEqual(3.46, stats['ref_p90'], 5)
        self.assertAlmostEqual(1, stats['p95'], 5)
        self.assertAlmostEqual(3.58, stats['ref_p95'], 2)
        self.assertAlmostEqual(1, stats['min'], 5)
        self.assertAlmostEqual(1.1, stats['ref_min'], 5)
        self.assertAlmostEqual(1, stats['max'], 5)
        self.assertAlmostEqual(3.7, stats['ref_max'], 5)

        self.assertAlmostEqual(stats['rmse'] ** 2, stats['bias'] ** 2 + stats['unbiased_rmse'] ** 2, 5)

    def test_cleanup_1(self):
        model_values = ma.array(np.arange(1.0, 5.0, 1), mask=np.array([False, False, True, False])) # [1, --, 3, 4]
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        ref_values, model_values = harmonise(ref_values, model_values)

        # Note: assert_array_equals does not tests if masks are equal
        # and there is no dedicated method for this
        # so masks need to be tested separately

        assert_array_equal(np.array([1, 2, 3, 4]), model_values)
        assert_array_equal(np.array([False, False, True, False]), model_values.mask)

        assert_array_equal(np.array([1.1, 2.2, 2.9, 3.7]), ref_values)
        assert_array_equal(np.array([False, False, True, False]), ref_values.mask)

    def test_cleanup_2(self):
        model_values = np.array(np.arange(1.0, 5.0, 1)) # [1, 2, 3, 4]
        ref_values = ma.array(np.array([1.1, 2.2, 2.9, 3.7]), mask=np.array([True, False, False, False]))
        ref_values, model_values = harmonise(ref_values, model_values)

        # Note: assert_array_equals does not tests if masks are equal
        # and there is no dedicated method for this
        # so masks need to be tested separately

        assert_array_equal(np.array([1, 2, 3, 4]), model_values)
        assert_array_equal(np.array([True, False, False, False]), model_values.mask)

        assert_array_equal(np.array([1.1, 2.2, 2.9, 3.7]), ref_values)
        assert_array_equal(np.array([True, False, False, False]), ref_values.mask)

    def test_cleanup_3(self):
        model_values = ma.array(np.arange(1.0, 5.0, 1), mask=np.array([False, False, True, False])) # [1, 2, --, 4]
        ref_values = ma.array([1.1, 2.2, 2.9, 3.7], mask=np.array([True, False, False, False]))
        ref_values, model_values = harmonise(ref_values, model_values)

        # Note: assert_array_equals does not tests if masks are equal
        # and there is no dedicated method for this
        # so masks need to be tested separately

        assert_array_equal(np.array([1.0, 2.0, 3.0, 4.0]), model_values)
        assert_array_equal(np.array([True, False, True, False]), model_values.mask)

        assert_array_equal(np.array([1.1, 2.2, 2.9, 3.7]), ref_values)
        assert_array_equal(np.array([True, False, True, False]), ref_values.mask)

    def test_extract_values(self):
        matchups = [
            Matchup([0, 0, 0, 0], [1261440000, 0.001, 55.2, 5.3], ReferenceRecord(0, 55.21, 5.31, 1261440250, 0.0012)),
            Matchup([0, 0, 0, 1], [1261440000, 0.001, 55.2, 5.8], ReferenceRecord(1, 55.8, 5.72, 1261440300, 0.0013))
        ]
        matchups[0].add_variable_value('chl_ref', np.nan)
        matchups[1].add_variable_value('chl_ref', 0.2)
        matchups[0].add_variable_value('chl', 0.1111)
        matchups[1].add_variable_value('chl', 0.2111)

        ref, model = extract_values(matchups, 'chl_ref', 'chl')
        assert_almost_equal(ref, np.ma.array([np.nan, 0.2], mask=[True, False]))
        assert_almost_equal(model, np.ma.array([0.1111, 0.2111], mask=[False, False]))