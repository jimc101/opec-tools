import os
import unittest
from src.main.python.Main import parse_arguments, DefaultAlgorithmSpec

class MainTest(unittest.TestCase):

    def test_parsing(self):
        args = parse_arguments(["-a /path/to/algorithm/spec.ini", "-o /path/to/target/directory", "-p target_prefix", "MyModelOutput.nc"])
        self.assertEqual("/path/to/algorithm/spec.ini", args.a.lstrip().rstrip())
        self.assertEqual("/path/to/target/directory", args.o.lstrip().rstrip())
        self.assertEqual("target_prefix", args.p.lstrip().rstrip())
        self.assertEqual("MyModelOutput.nc", args.path.lstrip().rstrip())

    def test_default_values(self):
        args = parse_arguments(["MyModelOutput.nc"])
        self.assertEqual("MyModelOutput.nc", args.path.lstrip().rstrip())
        self.assertIsInstance(args.a, DefaultAlgorithmSpec)
        self.assertEqual(os.getcwd(), args.o)
        self.assertEqual("benchmark_", args.p)

    def test_usage(self):
        message = ""
        try:
            parse_arguments("")
        except ValueError, e:
            message = e.message

        self.assertTrue(message.__contains__("usage:"))
        self.assertTrue(message.__contains__("[-a Algorithm specification file]"))
        self.assertTrue(message.__contains__("[-o Target directory]"))
        self.assertTrue(message.__contains__("[-p Target prefix]"))
        self.assertTrue(message.__contains__("<path>"))
        self.assertFalse(message.__contains__("Ruebennase"))