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
from opec.Matchup import Matchup
from opec.MatchupEngine import ReferenceRecord

class Matchup_test(TestCase):

    def test_string(self):
        cell_position = [0, 0, 0, 0]
        spacetime_position = [300000, 0.12, 89.99, 179.99]
        rr = ReferenceRecord(0, 88.12, 178.24, 300100, 0.13)
        m = Matchup(cell_position, spacetime_position, rr)
        self.assertEqual('cell_position: [0, 0, 0, 0], spacetime_position: [300000, 0.12, 89.99, 179.99], reference_record: lat: 88.12, lon: 178.24, depth: 0.13, record_number: 0, time: 300100, values: {}',
            m.__str__())
