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
import os

from unittest import TestCase
from opec.Data import Data
from opec.ReferenceRecordsFinder import ReferenceRecordsFinder

class ReferenceRecordsFinder_test(TestCase):

    def setUp(self):
        self.path = os.path.dirname(os.path.realpath(__file__)) + '/../'
        self.data = Data(self.path + 'resources/test.nc')

    def test_find_reference_records(self):
        rrf = ReferenceRecordsFinder(self.data)
        reference_records = rrf.find_reference_records()
        self.assertEqual(3, len(reference_records))
        self.assertAlmostEqual(55.21, reference_records[0].lat, 4)
        self.assertAlmostEqual(55.8, reference_records[1].lat, 4)
        self.assertAlmostEqual(56.12, reference_records[2].lat, 4)

        self.assertAlmostEqual(5.31, reference_records[0].lon, 4)
        self.assertAlmostEqual(5.72, reference_records[1].lon, 4)
        self.assertAlmostEqual(12.35, reference_records[2].lon, 4)

        self.assertAlmostEqual(0.0012, reference_records[0].depth, 4)
        self.assertAlmostEqual(0.0013, reference_records[1].depth, 4)
        self.assertAlmostEqual(0.0021, reference_records[2].depth, 4)

        self.assertAlmostEqual(1261440250, reference_records[0].time, 4)
        self.assertAlmostEqual(1261440300, reference_records[1].time, 4)
        self.assertAlmostEqual(1261447000, reference_records[2].time, 4)

    def test_find_reference_records_no_depth(self):
        self.data = Data(self.path + 'resources/test_without_depth.nc')
        rrf = ReferenceRecordsFinder(self.data)
        reference_records = rrf.find_reference_records()
        self.assertEqual(3, len(reference_records))

    def test_find_reference_records_gridded(self):
        self.data = Data(self.path + 'resources/ogs_test_smaller.nc')
        rrf = ReferenceRecordsFinder(self.data)
        reference_records = rrf.find_reference_records()
        self.assertEqual(41 * 80, len(reference_records))