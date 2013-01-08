import os
import unittest
from numpy.core.numeric import array
from experimental.taylor import exportTaylorDiagram

class NetCDFFacadeTest(unittest.TestCase):

    def setUp(self):
        self.targetFile = "../resources/taylor_test.png"

    def testExportTaylorDiagram(self):
        values = array(range(1, 5, 1)) # [1, 2, 3, 4]
        referenceData = array([1.1, 1.9, 3.01, 4.0])
#        print(Processor.rmsd(referenceData, values))
        exportTaylorDiagram(self.targetFile, values, referenceData)

    def tearDown(self):
        pass
#        os.remove(self.targetFile)