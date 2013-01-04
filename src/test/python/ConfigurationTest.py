from unittest import TestCase
from src.main.python.Configuration import global_config

class ConfigurationTest(TestCase):

    def setUp(self):
        self.config_1 = global_config()
        self.config_2 = global_config()

    def test_singularity(self):
        self.assertEqual(self.config_1, self.config_2)

    def test_singularity_2(self):
        global_config().alpha = 4
        self.assertEqual(4, global_config().alpha)