import unittest
from src.main.python.Main import parse_arguments

class MainTest(unittest.TestCase):

    def test_parsing(self):
        args = parse_arguments(["-a /path/to/configuration.ini", "-o /path/to/target/directory", "-p target_prefix", "-v chl_ref:chl sst_ref:sst", "MyModelOutput.nc"])
        self.assertEqual("/path/to/configuration.ini", args.a.lstrip().rstrip())
        self.assertEqual("/path/to/target/directory", args.o.lstrip().rstrip())
        self.assertEqual("target_prefix", args.p.lstrip().rstrip())
        self.assertEqual("MyModelOutput.nc", args.path.lstrip().rstrip())
        self.assertEqual([['chl_ref', 'chl'], ['sst_ref', 'sst']], args.v)

    def test_default_values(self):
        args = parse_arguments(["MyModelOutput.nc"])
        self.assertEqual("MyModelOutput.nc", args.path.lstrip().rstrip())
        self.assertIsNone(args.o)
        self.assertIsNone(args.p)

    def test_usage(self):
        message = ""
        try:
            parse_arguments("")
        except ValueError as e:
            message = e.args[0]

        self.assertTrue(message.__contains__("usage:"))
        self.assertTrue(message.__contains__("[-a Algorithm specification file]"))
        self.assertTrue(message.__contains__("[-o Target directory]"))
        self.assertTrue(message.__contains__("[-p Target prefix]"))
        self.assertTrue(message.__contains__("<path>"))
        self.assertFalse(message.__contains__("Big-Nose-City"))