import itertools
import unittest
from impl.CountCollections import CountDict
from impl.ProbRegressor import RegressOutputFile
from impl.RandomFetcher import *
from impl.OffenseFetcher import *
from impl.WetAnalysis import *
from impl.WetSteps import *

class Test_regression(unittest.TestCase):
    def setUp(self):
        # reset changeable global variables
        NONNEGATIVITY(False)
        FULL_DATASET(False)
        OUTPUT_FILENAME("zzzdefault.csv")
        MODEL_NAME("baseline")
        MAX_CLIQUE_SIZE(3)
        MU_COUNT(1)
        THETA_COUNT(1)
        
        # reset classes with persistent state
        RegressOutputFile.rof = None
        
        self.probSeparator: ProbSeparator = ProbSeparator()

    def pureLoad(self, data: list[dict]):
        for datum, index in zip(data, range(len(data))):
            datum = dict(datum)
            
            datum[-1] = datum["dependentVar"]
            
            workingTuple = tuple(value for key, value in datum.items() if isinstance(key, int) and key > 0)
            
            for result in [True, False]:
                self.probSeparator.add(index, workingTuple, result, datum[result])
    
    def baselineLoad(self, data: list[dict]):
        for datum, index in zip(data, range(len(data))):
            datum = dict(datum)
            
            proportionTrue = datum["dependentVar"]
            datum[True] = datum["weight"] * proportionTrue
            datum[False] = datum["weight"] * (1 - proportionTrue)
            
            workingTuple = tuple(value for key, value in datum.items() if isinstance(key, int))
            
            for result in [True, False]:
                self.probSeparator.add(index, workingTuple, result, datum[result])/
        
    # https://www.sciencedirect.com/science/article/pii/S016412122100159X

    def test_A(self):
        d = "dependentVar"
        w = "weight"
        
        workingList = [
            {2:1, 3:1, d:2, w:1},
            {2:2, 3:1, d:3, w:1},
            {2:3, 3:1, d:4, w:1},
            {2:1, 3:2, d:3, w:1},
            {2:2, 3:2, d:4, w:1},
            {2:3, 3:2, d:5, w:1},
            {2:1, 3:3, d:4, w:1},
            {2:2, 3:3, d:5, w:1}
        ]
        
        MODEL_NAME("baseline")
        
        self.baselineLoad(workingList)
        self.probSeparator.regress()
        


if __name__ == '__main__':
    unittest.main()
