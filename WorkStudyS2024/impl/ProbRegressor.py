import csv
from fractions import Fraction
import math
import random
from statistics import LinearRegression
import pandas as pd
from sklearn import linear_model
from statsmodels.regression.linear_model import OLSResults
from impl.CountCollections import CountDict, CountList
from impl.GlobalConsts import *
from impl.WetClique import WetClique

import statsmodels.api as sm

class ProbSeparator:
    def __init__(self, proportionTest: float = 0.15, probRecovery: float = 0) -> None:
        self.probRecovery: float = probRecovery

        self.proportionTest: float = proportionTest
        self.testSet: set[str] = set()
        
        self.trainDataCollector: ProbRegressor = ProbRegressor()
        self.testDataCollector: ProbRegressor = ProbRegressor()
        
    def initTestSet(self, allNames: list[str]) -> None:
        if self.proportionTest == 0: return

        random.shuffle(allNames)
        
        numTest: int = round(self.proportionTest * len(allNames))
        
        # numTest is clamped to [1, len(allNames)-1]
        numTest = sorted((1, numTest, len(allNames)-1))[1]
        
        self.testSet = set()
        for index in range(numTest):
            self.testSet.add(allNames[index])

    def add(self, vertexName, workingTuple: tuple, result: bool, weight: int = 1) -> None:
        if vertexName in self.testSet:
            self.testDataCollector.add(workingTuple, result, weight)
        else:
            self.trainDataCollector.add(workingTuple, result, weight)
            
    def regress(self, verbose: bool = False, *, bigTheta: float = None) -> None:
        trainModel = self.trainDataCollector.regress(verbose, bigTheta=bigTheta)
        trainData = self.trainDataCollector.linearDataset(bigTheta=bigTheta)
        testData = self.testDataCollector.linearDataset(bigTheta=bigTheta)

        outputDict = RegressOutputFile.interpretData(trainModel, trainData, testData, self.probRecovery, bigTheta=bigTheta)
        
        rof = RegressOutputFile.getROF()
        rof.logData(trainModel, trainData, testData, self.probRecovery, bigTheta=bigTheta)
        
class RegressOutputFile:
    rof: "RegressOutputFile" = None
    
    @classmethod
    def getROF(cls) -> "RegressOutputFile":
        if cls.rof == None:
            cls.rof = RegressOutputFile(OUTPUT_FILENAME())
        return cls.rof

    def __init__(self, filename: str) -> None:

        self.filename = OUTPUT_DATA_PREFIX + filename
        
        self.fieldnames = ["score", "cross-score"]
            
        if MODEL_NAME() == "baseline":
            self.fieldnames.append("beta_0")
            for size in SIZE_RANGE():
                self.fieldnames.append("beta_" + str(size - 1))
            self.fieldnames.insert(0, "mu")

        if MODEL_NAME() == "hypergraph":
            self.fieldnames.append("lambda_I")
            self.fieldnames.append("lambda_J<")
            self.fieldnames.append("lambda_J>=")
            self.fieldnames.insert(0, "delta_I")
            self.fieldnames.insert(1, "theta'_J")
        
        with open(self.filename, "w", newline="") as outputFile:
            writer = csv.DictWriter(outputFile, fieldnames=self.fieldnames)
            if MODEL_NAME() in {"baseline", "hypergraph"}:
                writer.writeheader()
            
    @classmethod
    def interpretData(cls, trainModel, trainData, testData, probRecovery: float = 0, *, bigTheta: float = None) -> dict[str]:
        def interpretDatum(iota: float) -> float:
            if MODEL_NAME() == "pure":
                return iota
            
            beta: float = 1 - 2**(-iota)
            
            # verify inverse
            testIota = -math.log2(1-beta)
            assert abs(testIota - iota) < 1e-11

            return beta

        if MODEL_NAME() in {"baseline", "hypergraph"}:
            output: dict[str] = {
                "score": trainModel.score(trainData["xVals"], trainData["yVals"], trainData["weights"]),
                "cross-score": "to be determined",
                "beta_0": interpretDatum(trainModel.intercept_)
            }
        
            try:
                output["cross-score"] = trainModel.score(testData["xVals"], testData["yVals"], testData["weights"])
            except:
                output["cross-score"] = float("nan")
            
            for size in SIZE_RANGE():
                output["beta_" + str(size - 1)] = interpretDatum(trainModel.coef_[size - 2])
            
            output["mu"] = probRecovery
            
            if MODEL_NAME() == "hypergraph":
                output["theta'_J"] = bigTheta
                # convert baseline var names to that of hypergraph
                output["lambda_I"] = output.pop("beta_0")
                output["lambda_J<"] = output.pop("beta_1")
                output["lambda_J>="] = output.pop("beta_2")
                output["delta_I"] = output.pop("mu")
                
                assert len(output) == 7
            
            return output
        
        if MODEL_NAME() == "pure":
            return trainModel.summary()
    
    def logData(self, trainModel, trainData, testData, probRecovery: float = 0, *, bigTheta: float = None) -> None:
        with open(self.filename, "a", newline="") as outputFile:
            if MODEL_NAME() in {"baseline", "hypergraph"}:
                writer = csv.DictWriter(outputFile, fieldnames=self.fieldnames)
            
                row = type(self).interpretData(trainModel, trainData, testData, probRecovery, bigTheta=bigTheta)
                writer.writerow(row)
            if MODEL_NAME() == "pure":
                outputFile.write(str(trainModel.summary()))

class ProbRegressor:
    def __init__(self) -> None:
        self.probTable: CountDict = CountDict()
    
    # result is true iff transmission occurs
    def add(self, workingTuple: tuple, result: bool, weight: int = 1) -> None:
        # workingTuple = (lineCount, triCount)
        self.probTable.add(workingTuple, result, weight)
                
    def linearDataset(self, *, bigTheta: float = None) -> dict[list]:
        xVals: list[list[int]] = list()
        yVals: list[float] = list()
        weights: list[int] = list()
        
        key: CountList
        
        workingProbTable = self.probTable
        
        if MODEL_NAME() == "hypergraph":
            workingProbTable = CountDict()
            
            for key in self.probTable.allKeys():
                newKey: CountList = CountList()
                frac: Fraction
                for frac in key.allKeys():
                    # index is 2 or 3 to be compatible with baseline
                    index = 3 if frac >= bigTheta else 2
                    newKey.add(index, key.read(frac))
                workingProbTable.add(newKey, False, self.probTable.read(key, False))
                workingProbTable.add(newKey, True, self.probTable.read(key, True))

        for key in workingProbTable.allKeys():
            if MODEL_NAME() in {"baseline", "hypergraph"}:
                # calculate the probability of NOT infection
                numerator: int = workingProbTable.read(key, False)
                denominator: int = numerator + workingProbTable.read(key, True)
            
                # convert prob to surprisal
                try:
                    probNoInfect: float = numerator / denominator
                    surprisalNoInfect: float = -math.log2(probNoInfect)
                except:
                    continue

                xVals.append([key.read(x) for x in SIZE_RANGE()])
                yVals.append(surprisalNoInfect)
                weights.append(denominator)
            if MODEL_NAME() == "pure":
                xVals.append([workingProbTable.read(key, x) for x in SIZE_RANGE()])
                yVals.append(workingProbTable.read(key, -1))
                weights.append(1)
            
        return dict(
            xVals=xVals,
            yVals=yVals,
            weights=weights
        )
        
    def regress(self, verbose: bool = False, *, bigTheta: float = None) -> LinearRegression:
        linearDataset = self.linearDataset(bigTheta=bigTheta)
        xVals: list[list[int]] = linearDataset["xVals"]
        yVals: list[float] = linearDataset["yVals"]
        weights: list[int] = linearDataset["weights"]
        
        if MODEL_NAME() in {"baseline", "hypergraph"}:
            model = linear_model.LinearRegression(positive=NONNEGATIVITY())
            try:
                model.fit(xVals, yVals, weights)
            except:
                pass
        
            if verbose:
                for i,j,k in sorted(zip(xVals, yVals, weights)):
                    print(i, j, k)
                print()
                print(model.coef_)
                print(model.intercept_)
                print(model.score(xVals, yVals, weights))
            
            return model
        
        if MODEL_NAME() == "pure":
            # take transpose of xVals
            xVals = [list(x) for x in zip(*xVals)]
            
            # convert xVals, yVals to collectedData: dict
            collectedData = {
                ("beta_"+str(x-1)):y for x,y in zip(SIZE_RANGE(), xVals)
            }
            collectedData["numOffenses"] = yVals

            # debugList = [x for x in collectedData["beta_1"]]
            # debugList.sort()
            # print(debugList)
            
            # print()
            # print()
            # print()
            # print()

            # debugList = [x for x in collectedData["beta_2"]]
            # debugList.sort()
            # print(debugList)
            
            df = pd.DataFrame(collectedData)
            
            y = df["numOffenses"]
            x = df[["beta_"+str(x-1) for x in SIZE_RANGE()]]
            x = sm.add_constant(x)
            
            model: OLSResults = sm.OLS(y, x).fit()
            
            x = df[["beta_"+str(x-1) for x in SIZE_RANGE()[:-1]]]
            x = sm.add_constant(x)
            
            reducedModel: OLSResults = sm.OLS(y, x).fit()
            
            # perform F test
            print("F test results:")
            print(model.compare_f_test(reducedModel))
            
            return model
                

        

        
        
