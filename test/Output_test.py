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

from datetime import datetime
from unittest import TestCase
import unittest
from opec import processor
from opec.matchup import Matchup
from opec.output import Output
from opec.configuration import Configuration
import os.path as path
import os as os
from opec.reference_records_finder import ReferenceRecord

class Output_test(TestCase):

    def setUp(self):
        self.config = Configuration(1, 1, 0, 12, 1234, 0.234)
        self.stats = processor.calculate_statistics([11, 9, 11.2, 10.5], [10, 10, 10, 10], 'chl', 'chl_ref', config=self.config)
        path = os.path.dirname(os.path.realpath(__file__)) + '/../'
        self.temp_filename = path + 'resources/test_output.csv'
        self.xml_target_file = path + 'resources/matchup_report.xml'

    def delete(self, file):
        if path.exists(file):
            os.remove(file)
            if path.exists(file):
                self.fail('Failed to delete {}'.format(file))

    def tearDown(self):
        self.delete(self.temp_filename)
        self.delete(self.xml_target_file)

    @unittest.skip('shall not run in production environment')
    def test_output_csv(self):
        output = Output(config=self.config)
        expected_result = []
        expected_result.append("##############################################################")
        expected_result.append("#")
        expected_result.append("# Benchmarking results")
        expected_result.append("#")
        expected_result.append("##############################################################")
        expected_result.append("#")
        expected_result.append("# Performed at {}".format(datetime.now().strftime('%b %d, %Y at %H:%M:%S')))
        expected_result.append("#")
        expected_result.append("# Number of matchups: 1")
        expected_result.append("#")
        expected_result.append("# Matchup criteria:")
        expected_result.append("#    Maximum geographic delta = 12.0 degrees")
        expected_result.append("#    Maximum time delta = 1234 seconds")
        expected_result.append("#    Maximum depth delta = 0.234 meters")
        expected_result.append("#")
        expected_result.append("# Algorithm parameters:")
        expected_result.append("#    ddof (delta degrees of freedom, used for computation of stddev) = 0")
        expected_result.append("#    alpha (used for percentile computation) = 1")
        expected_result.append("#    beta (used for percentile computation) = 1")
        expected_result.append("#")
        expected_result.append("# Statistics for variable 'chl' with reference 'chl_ref':")
        expected_result.append("")
        expected_result.append("rmse\t0.9605")
        expected_result.append("unbiased_rmse\t0.8613")
        expected_result.append("bias\t-0.425")
        expected_result.append("pbias\t-4.25")
        expected_result.append("corrcoeff\tnan")
        expected_result.append("reliability_index\t1.0417")
        expected_result.append("model_efficiency\tnan")
        expected_result.append("")
        expected_result.append("# Statistics of variable 'chl':")
        expected_result.append("")
        expected_result.append("min\t9")
        expected_result.append("max\t11.2")
        expected_result.append("mean\t10.425")
        expected_result.append("stddev\t0.8613")
        expected_result.append("median\t10.75")
        expected_result.append("p90\t11.14")
        expected_result.append("p95\t11.17")
        expected_result.append("")
        expected_result.append("# Statistics of variable 'chl_ref':")
        expected_result.append("")
        expected_result.append("min\t10")
        expected_result.append("max\t10")
        expected_result.append("mean\t10")
        expected_result.append("stddev\t0")
        expected_result.append("median\t10")
        expected_result.append("p90\t10")
        expected_result.append("p95\t10")

        matchups = [Matchup([0, 0, 0, 0], [300000, 0.12, 55.1, 5.3], ReferenceRecord(0, 5.4, 55.3, 300200, 0.11))]
        self.assertTrue(output.csv(self.stats, 'chl', 'chl_ref', matchups=matchups).startswith("\n".join(expected_result)))

    @unittest.skip('shall not run in production environment')
    def test_write_csv_file(self):
        output = Output()
        self.assertFalse(path.exists(self.temp_filename))
        output.csv(self.stats, 'Heidi', 'some_ref', target_file=self.temp_filename)
        self.assertTrue(path.exists(self.temp_filename))
        os.remove(self.temp_filename)
        self.assertFalse(path.exists(self.temp_filename))

    @unittest.skip('shall not run in production environment')
    def test_output_xhtml_multiple_stats(self):
        output = Output()
        matchup_1 = Matchup([0, 0, 0, 0], [300000, 0.12, 55.1, 5.3], ReferenceRecord(0, 5.4, 55.3, 300200, 0.11))
        matchup_2 = Matchup([0, 0, 0, 1], [300020, 0.54, 56.1, 5.7], ReferenceRecord(1, 5.8, 57.2, 300400, 0.12))
        matchups = [matchup_1, matchup_2]

        second_stats = processor.calculate_statistics([2.2, 3.8, 4.4, 9.2], [2, 3, 4, 3], 'sst', 'sst_ref', config=self.config)

        output.xhtml((self.stats, second_stats), matchups, self.xml_target_file)
