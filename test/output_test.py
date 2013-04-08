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
import unittest
from opec import processor
from opec.output import Output
import numpy as np

class Output_test(TestCase):

    @unittest.skip('no unit test')
    def test_output_csv(self):
        chl_ref_chl = ('chl', 'Ref_chl')
        chl_ref2_chl = ('chl', 'Ref2_chl')
        sst_ref_sst = ('sst', 'sst_reference')
        sst_sst = ('sst', 'sst')
        mappings = [chl_ref_chl, chl_ref2_chl, sst_ref_sst, sst_sst]

        statistics = {}
        statistics[chl_ref_chl] = processor.calculate_statistics(np.array([11, 9, 11.2, 10.5]), np.array([10, 10, 10, 10]), 'chl', 'Ref_chl')
        statistics[chl_ref2_chl] = processor.calculate_statistics(np.array([12, 2, 3, 5]), np.array([2, 3, 4, 6]), 'chl', 'Ref2_chl')
        statistics[sst_ref_sst] = processor.calculate_statistics(np.array([8, 9, 15, 4]), np.array([6, 8, 2, 1]), 'sst', 'Ref_sst')
        statistics[sst_sst] = processor.calculate_statistics(np.array([8, 10, 2, 55]), np.array([99, 5, 5, 23]), 'sst', 'sst')

        output = Output()
        output.csv(mappings, statistics, 10957, matchups=None, target_file='c:\\temp\\output\\benchmark\\test.csv')
