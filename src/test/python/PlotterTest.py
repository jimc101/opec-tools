import unittest
import numpy as np
from src.main.python import Processor
import src.main.python.Plotter as plotter

class PlotterTest(unittest.TestCase):

    def setUp(self):
        self.target_file = "../resources/taylor_test.png"

    def test_taylor_diagram(self):
        random = np.random.random(50)
        values = np.fromfunction(lambda x: np.ones([50]) + random, [50])
        reference_values = np.fromfunction(lambda x: np.cos(x), [50])
        stats = Processor.calculate_statistics(model_values=values, reference_values=reference_values)

        plotter.create_taylor_diagram(stats, self.target_file)

    def tearDown(self):
        pass
        #        os.remove(self.targetFile)