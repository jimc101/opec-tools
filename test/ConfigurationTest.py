import logging
import os
import unittest
from opec.Configuration import Configuration

class ConfigurationTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.cwd = os.getcwd()
        os.chdir('..')

    @classmethod
    def tearDownClass(self):
        os.chdir(self.cwd)

    def test_initialisation(self):
        c = Configuration(alpha=5, ddof=2, show_legend=False, write_taylor_diagrams=False, separate_matchups=False)
        self.assertEqual(5, c.alpha)
        self.assertEqual(1, c.beta)
        self.assertEqual(2, c.ddof)
        self.assertEqual(12, c.depth_delta)
        self.assertEqual(1, c.geo_delta)
        self.assertEqual(86400, c.time_delta)
        self.assertEqual(logging.INFO, c.log_level)
        self.assertEqual(False, c.zip)
        self.assertEqual(False, c.show_negative_corrcoeff)
        self.assertEqual(False, c.show_legend)
        self.assertEqual(os.getcwd(), c.target_dir)
        self.assertEqual('benchmark_', c.target_prefix)
        self.assertEqual('\t', c.separator)
        self.assertEqual(False, c.write_taylor_diagrams)
        self.assertEqual(None, c.log_file)
        self.assertEqual(True, c.write_csv)
        self.assertEqual(True, c.write_xhtml)
        self.assertEqual(False, c.separate_matchups)
        self.assertEqual(True, c.write_scatter_plots)

    def test_initialisation_by_file(self):
        c = Configuration(alpha=5, ddof=2, log_level='INFO', properties_file_name='./resources/test.properties')
        self.assertEqual(5, c.alpha)
        self.assertEqual(0.5, c.beta)
        self.assertEqual(2, c.ddof)
        self.assertEqual(3, c.depth_delta)
        self.assertEqual(1, c.geo_delta)
        self.assertEqual(200, c.time_delta)
        self.assertEqual(logging.INFO, c.log_level)    # does not appear in test.properties, so it is taken from default file
        self.assertEqual(False, c.zip)             # does not appear in test.properties, so it is taken from default file
        self.assertEqual(True, c.show_legend)
        self.assertEqual(False, c.show_negative_corrcoeff)             # does not appear in test.properties, so it is taken from default file
        self.assertEqual(os.getcwd(), c.target_dir)
        self.assertEqual('benchmark_', c.target_prefix)
        self.assertEqual(True, c.write_taylor_diagrams)
        self.assertEqual(None, c.log_file)
        self.assertEqual(False, c.write_csv)
        self.assertEqual(False, c.write_xhtml)
        self.assertEqual(True, c.separate_matchups)

    def test_wrong_log_level(self):
        self.assertRaises(RuntimeError, lambda: Configuration(log_level='LOG_EVERYTHING_PLEASE'))

    def test_disabled_log_level(self):
        c = Configuration(log_level='DISABLED')
        self.assertEqual(100, c.log_level)

    def test_log_file(self):
        c = Configuration(log_file='somewhere_to_log_into')
        self.assertEqual('somewhere_to_log_into', c.log_file)

    def test_split_up_criteria(self):
        c = Configuration(split_diagrams='nu')
        self.assertTrue(c.split_on_unit)
        self.assertTrue(c.split_on_name)

        c = Configuration(split_diagrams='')
        self.assertFalse(c.split_on_unit)
        self.assertFalse(c.split_on_name)

        c = Configuration()
        self.assertTrue(c.split_on_unit)
        self.assertFalse(c.split_on_name)

        self.assertRaises(ValueError, lambda: Configuration(split_diagrams='cowabunga!'))
        self.assertRaises(ValueError, lambda: Configuration(split_diagrams='cow'))
        self.assertRaises(ValueError, lambda: Configuration(split_diagrams='p'))
        self.assertRaises(ValueError, lambda: Configuration(split_diagrams='ssuv'))

    def test_max_bounds_for_target_diagram(self):
        c = Configuration()
        self.assertIsNone(c.target_diagram_bounds)

        c = Configuration(target_diagram_bounds=[-2.0, 5.0, -3.0, None])
        self.assertEqual(-2.0, c.target_diagram_bounds[0])
        self.assertEqual(5.0, c.target_diagram_bounds[1])
        self.assertEqual(-3.0, c.target_diagram_bounds[2])
        self.assertIsNone(c.target_diagram_bounds[3])


    def test_write_target_diagram(self):
        c = Configuration()
        self.assertTrue(c.write_target_diagram)

        c = Configuration(write_target_diagram=False)
        self.assertFalse(c.write_target_diagram)

    def test_normalise_target_diagram(self):
        c = Configuration()
        self.assertTrue(c.normalise_target_diagram)

        c = Configuration(normalise_target_diagram=False)
        self.assertFalse(c.normalise_target_diagram)