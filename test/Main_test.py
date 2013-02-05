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