import itertools
import unittest

from sklearn import linear_model
from statsmodels.regression.linear_model import OLSResults
import pandas as pd
import statsmodels.api as sm
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
        for datum in data:
            index = len(self.probSeparator.trainDataCollector.probTable.internalDict)
            
            # make deep copy to prevent clobbering data
            datum = dict(datum)
            
            datum[-1] = datum["dependentVar"]
            
            for key, count in datum.items():
                if isinstance(key, int):
                    self.probSeparator.add(index, index, key, count)
    
    def baselineLoad(self, data: list[dict]):
        for datum in data:
            index = len(self.probSeparator.trainDataCollector.probTable.internalDict)
            
            # make deep copy to prevent clobbering data
            datum = dict(datum)
            
            if not (-1 < datum["dependentVar"] < 1):
                self.skipTest()
            
            proportionFalse = datum["dependentVar"]
            adjustedProportionFalse = 2**(-proportionFalse)
            
            datum[False] = datum["weight"] * adjustedProportionFalse
            datum[True] = datum["weight"] * (1 - adjustedProportionFalse)
            
            workingCountList = CountList()
            for key, count in datum.items():
                if isinstance(key, int):
                    workingCountList.add(key, count)
            
            for result in [True, False]:
                self.probSeparator.add(index, workingCountList, result, datum[result])
                
    def hypergraphLoad(self, data: list[dict]):
        for datum in data:
            index = len(self.probSeparator.trainDataCollector.probTable.internalDict)
            
            # make deep copy to prevent clobbering data
            datum = dict(datum)
            
            if not (-1 < datum["dependentVar"] < 1):
                self.skipTest()
            
            proportionFalse = datum["dependentVar"]
            adjustedProportionFalse = 2**(-proportionFalse)
            
            datum[False] = datum["weight"] * adjustedProportionFalse
            datum[True] = datum["weight"] * (1 - adjustedProportionFalse)
            
            workingCountList = CountList()
            for key, count in datum.items():
                conversionDict = {
                    2: Fraction(0),
                    3: Fraction(1)
                }
                if key in conversionDict.keys():
                    workingCountList.add(conversionDict[key], count)
            
            for result in [True, False]:
                self.probSeparator.add(index, workingCountList, result, datum[result])
                
    def autoLoad(self, data: list[dict]):
        self.assertIn(MODEL_NAME(), ALL_MODELS.values())
        match MODEL_NAME():
            case "pure":
                self.pureLoad(data)
            case "baseline":
                self.baselineLoad(data)
            case "hypergraph":
                self.hypergraphLoad(data)

    def test_sanity(self):
        d = "dependentVar"
        w = "weight"
        
        workingList = [
            {2: 1, 3: 1, d: .2, w: 1},
            {2: 2, 3: 1, d: .3, w: 1},
            {2: 3, 3: 1, d: .4, w: 1},
            {2: 4, 3: 1, d: .5, w: 1},
            {2: 1, 3: 2, d: .3, w: 1},
            {2: 2, 3: 2, d: .4, w: 1},
            {2: 3, 3: 2, d: .5, w: 1},
            {2: 1, 3: 3, d: .4, w: 1},
            {2: 2, 3: 3, d: .5, w: 1},
            {2: 2.5, 3: 2.5, d: .5, w: 1}
        ]
        
        MODEL_NAME("baseline")
        
        self.baselineLoad(workingList)
        model: linear_model.LinearRegression = self.probSeparator.trainDataCollector.regress(verbose=True)
        
        self.assertAlmostEqual(0.1, model.coef_[0])
        self.assertAlmostEqual(0.1, model.coef_[1])
        self.assertAlmostEqual(0, model.intercept_)

    def test_mapping(self):
        workingList = [{2: x, 3: y, "dependentVar": random.random(), "weight": 1}
                       for x,y in itertools.product(range(4), repeat=2)]
        
        MODEL_NAME("baseline")
        
        self.baselineLoad(workingList)
        
        linearDataset = self.probSeparator.trainDataCollector.linearDataset()
        
        transposedDataset = list()
        for index in range(len(linearDataset["xVals"])):
            transposedDataset.append({k: v[index] for k,v in linearDataset.items()})
            
        print("workingList:")
        print(workingList)
        print("transposedDataset:")
        print(transposedDataset)

        for entryIn, entryOut in zip(workingList, transposedDataset, strict=True):
            self.assertAlmostEqual(entryIn["dependentVar"], entryOut["yVals"])
    
    # https://www.sciencedirect.com/science/article/pii/S016412122100159X
    
    def test_metamorphic(self):
        
        def getCoefs(model):
            if MODEL_NAME() == "pure":
                return (model.params[1:], model.params[0])
            if MODEL_NAME() in {"baseline", "hypergraph"}:
                return (model.coef_, model.intercept_)

        workingList = [{2: x, 3: y, "dependentVar": random.random(), "weight": 1}
                       for x,y in itertools.product(range(4), repeat=2)]
        
        # repeat all tests 16 times
        for _ in range(16):
            for modelName in ALL_MODELS.values():
                MODEL_NAME(modelName)
                
                print("model name:", modelName)
                self.autoLoad(workingList)
                
                sourceModel: linear_model.LinearRegression = self.probSeparator.trainDataCollector.regress(verbose=True, bigTheta=0.5)
                sourceCoefs, sourceIntercept = getCoefs(sourceModel)
                
                # save probSeparator's persistent state
                sourceProbInternalDict: CountDict = dict(self.probSeparator.trainDataCollector.probTable.internalDict)
                
                for relation in ["MR1.1", "MR1.2", "MR2.1", "MR2.2|2", "MR2.2|3", "MR3.1", "MR3.2|2", "MR3.2|3", "MR4.1", "MR4.2|2", "MR4.2|3", "MR5.1", "MR5.2", "MR6"]: 
                    # with self.subTest(modelName=modelName, relation=relation):
                        print("relation:", relation)
                        
                        # if relation ends in |2 or |3, set activeAxis accordingly
                        if relation[-2] == "|":
                            activeAxis = int(relation[-1])
                        else:
                            activeAxis = 0
                
                        self.assertEqual(len(self.probSeparator.trainDataCollector.probTable.internalDict), len(workingList))
                        
                        # default expected coefs, intercept. overwritten where required.
                        expectedCoefs = sourceCoefs
                        expectedIntercept = sourceIntercept

                        match relation:
                            case "MR1.1":
                                # add a datum on the fit plane. followUpModel should not change.
                                workingListAddendum = {2: random.uniform(0,5), 3: random.uniform(0,5), "weight": 1}

                                # solve for dependentVar using fit plane equation
                                workingListAddendum["dependentVar"] = (
                                    (workingListAddendum[2] * sourceCoefs[0])
                                    + (workingListAddendum[3] * sourceCoefs[1])
                                    + sourceIntercept 
                                )
                                
                                workingListReplacement = workingList + [workingListAddendum]
                                
                                #expectedCoefs = sourceCoefs            # redundant
                                #expectedIntercept = sourceIntercept    # redundant
                                
                            case "MR1.2":
                                # add a datum at the centroid. followUpModel should not change.
                                workingListAddendum = dict()
                                for key in {2,3,"dependentVar","weight"}:
                                    workingListAddendum[key] = sum(datum[key] for datum in workingList) / len(workingList)
                            
                                workingListReplacement = workingList + [workingListAddendum]
                                
                                #expectedCoefs = sourceCoefs            # redundant
                                #expectedIntercept = sourceIntercept    # redundant
                                
                            case "MR2.1":
                                # reflect data at "dependentVar". followUpModel should reverse all coefficients and intercept.
                                workingListReplacement = [{
                                    2: datum[2],
                                    3: datum[3],
                                    "dependentVar": -datum["dependentVar"],
                                    "weight": datum["weight"]
                                } for datum in workingList]
                                
                                expectedCoefs = [-x for x in sourceCoefs]
                                expectedIntercept = -sourceIntercept
                                
                            case "MR2.2|2" | "MR2.2|3":
                                # reflect data at "2" (resp. "3"). followUpModel should reverse only "2" (resp. "3") coefficient.
                                workingListReplacement = [{
                                    2: datum[2] * (-1 if activeAxis == 2 else 1),
                                    3: datum[3] * (-1 if activeAxis == 3 else 1),
                                    "dependentVar": datum["dependentVar"],
                                    "weight": datum["weight"]
                                } for datum in workingList]
                        
                                expectedCoefs = [x * (-1 if activeAxis == i else 1) for x,i in zip(sourceCoefs, [2,3])]
                                #expectedIntercept = sourceIntercept    # redundant
                            
                            case "MR3.1":
                                # scale data at "dependentVar". followUpModel should scale all coefficients and intercept.
                                scaleFactor = random.uniform(0.5, 1)
                                workingListReplacement = [{
                                    2: datum[2],
                                    3: datum[3],
                                    "dependentVar": datum["dependentVar"] * scaleFactor,
                                    "weight": datum["weight"]
                                } for datum in workingList]
                                
                                expectedCoefs = [x * scaleFactor for x in sourceCoefs]
                                expectedIntercept = sourceIntercept * scaleFactor
                        
                            case "MR3.2|2" | "MR3.2|3":
                                # scale data at "2" (resp. "3"). followUpModel should inversely scale only "2" (resp. "3") coefficient.
                                scaleFactor = random.uniform(0.5, 2)
                                workingListReplacement = [{
                                    2: datum[2] * (scaleFactor if activeAxis == 2 else 1),
                                    3: datum[3] * (scaleFactor if activeAxis == 3 else 1),
                                    "dependentVar": datum["dependentVar"],
                                    "weight": datum["weight"]
                                } for datum in workingList]

                                expectedCoefs = [x / (scaleFactor if activeAxis == i else 1) for x,i in zip(sourceCoefs, [2,3])]
                                #expectedIntercept = sourceIntercept    # redundant

                            case "MR4.1":
                                # translate data at "dependentVar". followUpModel should translate only at intercept.
                                translateDist = random.uniform(-1, 0)
                                workingListReplacement = [{
                                    2: datum[2],
                                    3: datum[3],
                                    "dependentVar": datum["dependentVar"] + translateDist,
                                    "weight": datum["weight"]
                                } for datum in workingList]
                                
                                #expectedCoefs = sourceCoefs            # redundant
                                expectedIntercept = sourceIntercept + translateDist
                        
                            case "MR4.2|2" | "MR4.2|3":
                                coefLoc = {2:0, 3:1}[activeAxis]
                                # translate data at "2" (resp. "3"). followUpModel should translate at intercept based on "2" (resp. "3") coefficient.
                                translateDist = random.uniform(-1, 1)
                                workingListReplacement = [{
                                    2: datum[2] + (translateDist if activeAxis == 2 else 0),
                                    3: datum[3] + (translateDist if activeAxis == 3 else 0),
                                    "dependentVar": datum["dependentVar"],
                                    "weight": datum["weight"]
                                } for datum in workingList]
                                    
                                #expectedCoefs = sourceCoefs            # redundant
                                expectedIntercept = sourceIntercept - (translateDist * sourceCoefs[coefLoc])
                            
                            case "MR5.1":
                                # shuffle data points. followUpModel should not change.
                                workingListReplacement = list(workingList)
                                random.shuffle(workingList)
                                
                                #expectedCoefs = sourceCoefs            # redundant
                                #expectedIntercept = sourceIntercept    # redundant
                        
                            case "MR5.2":
                                # swap components of data points. followUpModel should swap components accordingly
                                workingListReplacement = [{
                                    2: datum[3],
                                    3: datum[2],
                                    "dependentVar": datum["dependentVar"],
                                    "weight": datum["weight"]
                                } for datum in workingList]

                                expectedCoefs = reversed(sourceCoefs)
                                #expectedIntercept = sourceIntercept    # redundant
                        
                            case "MR6":
                                theta = random.uniform(0, 2*math.pi)
                                # rotate components of data points. followUpModel should rotate components accordingly
                                workingListReplacement = [{
                                    2: (datum[2] * math.cos(theta)) - (datum[3] * math.sin(theta)),
                                    3: (datum[2] * math.sin(theta)) + (datum[3] * math.cos(theta)),
                                    "dependentVar": datum["dependentVar"],
                                    "weight": datum["weight"]
                                } for datum in workingList]

                                expectedCoefs = [(sourceCoefs[0] * math.cos(theta)) - (sourceCoefs[1] * math.sin(theta)),
                                                 (sourceCoefs[0] * math.sin(theta)) + (sourceCoefs[1] * math.cos(theta))]
                                #expectedIntercept = sourceIntercept    # redundant
                                
                            case _:
                                self.fail(relation + " " + "not found")
                                
                        # clear source data and replace with follow up data
                        self.probSeparator.trainDataCollector.probTable.internalDict = dict()
                        self.autoLoad(workingListReplacement)
                        followUpModel: linear_model.LinearRegression = self.probSeparator.trainDataCollector.regress(verbose=True, bigTheta=0.5)
                            
                        # compare obtained coefs with expected coefs
                        followUpCoefs, followUpIntercept = getCoefs(followUpModel)
                        for followUpCoef, expectedCoef in zip(followUpCoefs, expectedCoefs, strict=True):
                            self.assertAlmostEqual(followUpCoef, expectedCoef)
                        self.assertAlmostEqual(followUpIntercept, expectedIntercept)
                        
                        # restore probSeparator's persistent state
                        self.probSeparator.trainDataCollector.probTable.internalDict = dict(sourceProbInternalDict)
                    
                # reset classes with persistent state
                RegressOutputFile.rof = None
                self.probSeparator = ProbSeparator()
        


if __name__ == '__main__':
    unittest.main()
