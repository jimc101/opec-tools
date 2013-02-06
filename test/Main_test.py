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
from opec.Main import parse_arguments

class Main_test(unittest.TestCase):

    def test_parsing(self):
        args = parse_arguments(["-c /path/to/configuration.ini", "-o /path/to/target/directory", "-p target_prefix", "-v [chl:chl_ref,sst:sst_ref]", "MyModelOutput.nc"])
        self.assertEqual("/path/to/configuration.ini", args.config.lstrip().rstrip())
        self.assertEqual("/path/to/target/directory", args.output_dir.lstrip().rstrip())
        self.assertEqual("target_prefix", args.prefix.lstrip().rstrip())
        self.assertEqual("MyModelOutput.nc", args.path.lstrip().rstrip())
        self.assertEqual([['chl', 'chl_ref'], ['sst', 'sst_ref']], args.variable_mappings)

    def test_default_values(self):
        args = parse_arguments(["MyModelOutput.nc"])
        self.assertEqual("MyModelOutput.nc", args.path.lstrip().rstrip())
        self.assertIsNone(args.output_dir)
        self.assertIsNone(args.prefix)