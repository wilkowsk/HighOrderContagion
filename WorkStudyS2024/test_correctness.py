import itertools
import unittest
from impl.CountCollections import CountDict
from impl.ProbRegressor import RegressOutputFile
from impl.RandomFetcher import *
from impl.OffenseFetcher import *
from impl.WetAnalysis import *
from impl.WetSteps import *

class Test_comparative(unittest.TestCase):
    def randomizeData(self, numVertices: int, numCliques: int, numOffenses: int):
        fetcher = RandomFetcher(numVertices, numCliques, numOffenses)
        profileDict = fetcher.getProfileDict()
        complaintList = fetcher.getComplaintList(profileDict)
        allComplaintDates = fetcher.allComplaintDates(complaintList)

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

    def test_clique_formation(self):
        MODEL_NAME("pure")
        MAX_CLIQUE_SIZE(3)

        numTests:       int = 16
        numVertices:    int = 16
        numCliques:     int = 16
        
        probRecovery = 0.5
        
        class TestWetAnalysis(WetAnalysis):
            allPairs: set = set()
                
            @classmethod
            def atLoopEnd(cls, week):
                for row in week:
                    vertices = [WetClique.allVertices[x["UID"]] for x in row["accusation"]]
                    
                    for v1,v2 in itertools.combinations(vertices, 2):
                        pair = frozenset({v1, v2})
                        cls.allPairs.add(pair)
                
                for v1,v2 in itertools.combinations(WetClique.allVertices.values(), 2):
                    totalCoef: int = 0
                    
                    clique: WetClique
                    for clique in v1.inCliques & v2.inCliques:
                        totalCoef += clique.coef
                        
                    expectedCoef = 1 if frozenset({v1,v2}) in cls.allPairs else 0

                    self.assertEqual(totalCoef,expectedCoef)
                    
        # RAND_DATA_PREFIX loads the fetcher with random data
        # if the test fails, the fetcher persists for the next test run
        fetcher = OffenseFetcher(prefix = RAND_DATA_PREFIX)
        
        for _ in range(numTests):
            TestWetAnalysis.tabulate(fetcher, probRecovery, doRegress=False)
            
            # randomize fetcher for next test
            self.randomizeData(numVertices, numCliques, numCliques * 3)
            
    def test_hyperedge_formation(self):
        MODEL_NAME("hypergraph")
        MAX_CLIQUE_SIZE(3)

        numTests:       int = 16
        numVertices:    int = 16
        numCliques:     int = 16
        
        probRecovery = 0.5
        
        class TestWetAnalysis(WetAnalysis):
            allPairs: CountList = CountList()
                
            @classmethod
            def atLoopEnd(cls, week):
                for row in week:
                    vertices = [WetClique.allVertices[x["UID"]] for x in row["accusation"]]
                    
                    for v1,v2 in itertools.combinations(vertices, 2):
                        pair = frozenset({v1, v2})
                        cls.allPairs.add(pair)
                
                for v1,v2 in itertools.combinations(WetClique.allVertices.values(), 2):
                    pair = frozenset({v1, v2})
                    totalCoef: int = 0
                    
                    clique: WetClique
                    for clique in v1.inCliques & v2.inCliques:
                        totalCoef += clique.coef
                        
                    expectedCoef = cls.allPairs.read(pair)

                    self.assertEqual(totalCoef,expectedCoef)
                    
        # RAND_DATA_PREFIX loads the fetcher with random data
        # if the test fails, the fetcher persists for the next test run
        fetcher = OffenseFetcher(prefix = RAND_DATA_PREFIX)
        
        for _ in range(numTests):
            TestWetAnalysis.tabulate(fetcher, probRecovery, doRegress=False)
            
            # randomize fetcher for next test
            self.randomizeData(numVertices, numCliques, numCliques * 3)
            
    def test_sample_equivalence(self):
        MODEL_NAME("baseline")
        MAX_CLIQUE_SIZE(3)

        numTests:       int = 16
        numVertices:    int = 16
        numCliques:     int = 16
        
        probRecovery = 1
        
        class TestWetAnalysis(WetAnalysis):
            extantWetSteps: WetSteps = None
            expectedProbTable: CountDict = CountDict()
            
            @classmethod
            def beforeLoop(cls, ws):
                cls.extantWetSteps = ws
                # print(ws)
                
            @classmethod
            def atLoopBegin(cls, week):
                justInfected: set = set()

                for row in week:
                    vertices = [WetClique.allVertices[x["UID"]] for x in row["accusation"]]
                    
                    justInfected |= set(vertices)
                
                vertex: WetClique
                for vertex in WetClique.allVertices.values():
                    isCounted: bool = True
                    if vertex.virginity:
                        # virgin vertices cannot get infected
                        isCounted = False
                    if vertex.isInfected():
                        # infected vertices cannot get infected again
                        isCounted = False
                        
                    if isCounted:
                        cls.expectedProbTable.add(vertex.riskCounts.getState(), (vertex in justInfected), 1)

                actualProbTable = TestWetAnalysis.extantWetSteps.probSeparator.trainDataCollector.probTable
                print("Actual prob table:")
                for entry in actualProbTable.internalDict.items():
                    print(entry[0], entry[1])
        
        # self.randomizeData(numVertices, numCliques, numCliques * 3)
                    
        # RAND_DATA_PREFIX loads the fetcher with random data
        # if the test fails, the fetcher persists for the next test run
        fetcher = OffenseFetcher(prefix = RAND_DATA_PREFIX)
        #fetcher = OffenseFetcher(profileCond = lambda row: row["UID"][-1] == "5")            
        
        for _ in range(numTests):
            TestWetAnalysis.tabulate(fetcher, probRecovery, doRegress=False)
            
            expectedProbTable = TestWetAnalysis.expectedProbTable
            print("Expected prob table:")
            for entry in expectedProbTable.internalDict.items():
                print(entry[0], entry[1])
                
            actualProbTable = TestWetAnalysis.extantWetSteps.probSeparator.trainDataCollector.probTable
            print("Actual prob table:")
            for entry in actualProbTable.internalDict.items():
                print(entry[0], entry[1])
                
            # subtract actualProbTable from expectedProbTable, expect zero result
            for key in actualProbTable.internalDict.keys():
                for value in actualProbTable.internalDict[key].keys():
                    count = actualProbTable.read(key, value)
                    expectedProbTable.add(key, value, -count)
                    
            for key in expectedProbTable.internalDict.keys():
                for value in expectedProbTable.internalDict[key].keys():
                    count = expectedProbTable.read(key, value)
                    # if key.internalDict != dict():
                    if True:
                        self.assertEqual(count, 0)
            
            # randomize fetcher for next test
            self.randomizeData(numVertices, numCliques, numCliques * 3)

    def test_hypergraph_sample_equivalence(self):
        MODEL_NAME("hypergraph")
        MAX_CLIQUE_SIZE(3)

        numTests:       int = 16
        numVertices:    int = 16
        numCliques:     int = 16
        
        probRecovery = 1
        
        class TestWetAnalysis(WetAnalysis):
            extantWetSteps: WetSteps = None
            expectedProbTable: CountDict = CountDict()
            
            @classmethod
            def beforeLoop(cls, ws):
                cls.extantWetSteps = ws
                # print(ws)
                
            @classmethod
            def atLoopBegin(cls, week):
                justInfected: set = set()

                for row in week:
                    vertices = [WetClique.allVertices[x["UID"]] for x in row["accusation"]]
                    
                    justInfected |= set(vertices)
                
                vertex: WetClique
                for vertex in WetClique.allVertices.values():
                    isCounted: bool = True
                    if vertex.virginity:
                        # virgin vertices cannot get infected
                        isCounted = False
                    if vertex.isInfected():
                        # infected vertices cannot get infected again
                        isCounted = False
                        
                    if isCounted:
                        cls.expectedProbTable.add(vertex.riskCounts.getState(), (vertex in justInfected), 1)

                actualProbTable = TestWetAnalysis.extantWetSteps.probSeparator.trainDataCollector.probTable
                print("Actual prob table:")
                for entry in actualProbTable.internalDict.items():
                    print(entry[0], entry[1])
        
        # self.randomizeData(numVertices, numCliques, numCliques * 3)
                    
        # RAND_DATA_PREFIX loads the fetcher with random data
        # if the test fails, the fetcher persists for the next test run
        fetcher = OffenseFetcher(prefix = RAND_DATA_PREFIX)
        #fetcher = OffenseFetcher(profileCond = lambda row: row["UID"][-1] == "5")            
        
        for _ in range(numTests):
            TestWetAnalysis.tabulate(fetcher, probRecovery, doRegress=False)
            
            expectedProbTable = TestWetAnalysis.expectedProbTable
            print("Expected prob table:")
            for entry in expectedProbTable.internalDict.items():
                print(entry[0], entry[1])
                
            actualProbTable = TestWetAnalysis.extantWetSteps.probSeparator.trainDataCollector.probTable
            print("Actual prob table:")
            for entry in actualProbTable.internalDict.items():
                print(entry[0], entry[1])
                
            # subtract actualProbTable from expectedProbTable, expect zero result
            for key in actualProbTable.internalDict.keys():
                for value in actualProbTable.internalDict[key].keys():
                    count = actualProbTable.read(key, value)
                    expectedProbTable.add(key, value, -count)
                    
            for key in expectedProbTable.internalDict.keys():
                for value in expectedProbTable.internalDict[key].keys():
                    count = expectedProbTable.read(key, value)
                    # if key.internalDict != dict():
                    if True:
                        self.assertEqual(count, 0)
            
            # randomize fetcher for next test
            self.randomizeData(numVertices, numCliques, numCliques * 3)
    
if __name__ == '__main__':
    unittest.main()
