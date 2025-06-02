import csv
from datetime import date
from fractions import Fraction
import math
import random

from numpy import linspace
from impl.CountCollections import CountList
from impl.ProbRegressor import ProbSeparator
from impl.WetClique import WetClique

from impl.GlobalConsts import *

import networkx as nx

class WetSteps:
    
    def __init__(self):
        pass
        
    def ApplyDeltas(self, collection, hasFormer: bool, currentDate, isolatedVertices: list[WetClique] = list()):
        
        augmentedCollection = list(collection)
        
        # add None; special cases treat it as a set containing isolatedVertices
        augmentedCollection.append(None)
        
        for clique in augmentedCollection:
            
            currentContribsDict = clique.endangerDict(hasFormer=hasFormer) if clique else {x: CountList() for x in isolatedVertices}
            if hasFormer:
                formerContribsDict = clique.endangerDict(currentDate, hasFormer=hasFormer) if clique else {x: CountList() for x in isolatedVertices}

            for vertex in clique.vertices if clique else isolatedVertices:
                
                # log former value of riskCounts
                if not vertex.infectedBefore(currentDate):
                    weight: int = (currentDate - vertex.riskLastChanged) // DATE_RES
                    self.probSeparator.add(vertex.name, vertex.riskCounts.getState(), False, weight)
                
                    if VERBOSE:
                        print(vertex.name, "from", vertex.riskLastChanged, "(", weight, "timesteps", "),", False)
                        print("   ", vertex.riskCounts.getState())
                    
                # update riskCounts
                
                vertex.riskCounts.update(currentContribsDict[vertex])
                if hasFormer:
                    vertex.riskCounts.update(formerContribsDict[vertex], reverse=True)
                vertex.riskLastChanged = currentDate
                
    def A_Init(self, fetcher, probRecovery):
        
        WetClique.reset()
    
        probSeparator: ProbSeparator = ProbSeparator(
            proportionTest=0,           # TODO: take 15% of officers to be the test case
            probRecovery=probRecovery
        )

        profileDict: dict = fetcher.getProfileDict()
        complaintList: list = fetcher.getComplaintList(profileDict)
    
        probSeparator.initTestSet([row["UID"] for row in profileDict.values()])
    
        row: dict
        for row in profileDict.values():
            # populate vertices
            uid = row["UID"]
            vertex = WetClique(uid)       
    
        currentDate = date.fromisoformat(DATE_INITIAL)
        thresholdDate = currentDate + DATE_RES
    
        weeklyList: list = list()
        intraweekList: list = list()
    
        # initialize weeklyList
    
        row: dict
        for row in complaintList:
        
            while date.fromisoformat(row["complaint"]["incident_date"]) >= thresholdDate:
                currentDate = thresholdDate
                thresholdDate = currentDate + DATE_RES
            
                weeklyList.append(intraweekList)
                intraweekList = list()
            
            intraweekList.append(row)
    
        weeklyList.append(intraweekList)
            
        self.probSeparator = probSeparator
        return weeklyList

    def B1_Infect(self, week, currentDate):
        # 1. infect vertices
        # note: vertices are infected only if they offend during this timestep
        # note: do this step before populating cliques to avoid a self-causing infection
        
        justInfected: list = list()
        
        if PROGRESS_SUBCHECK: print("A. infect vertices")
        if VERBOSE:
            print("Infected beforehand:")
            print([x.name for x in WetClique.allVertices.values() if x.isInfected()])
            print(".")
        row: dict
        for row in week:
            ids = [x["UID"] for x in row["accusation"]]
            vertices = set([WetClique.allVertices[x] for x in ids])
            
            vertex: WetClique
            for vertex in vertices:
                if vertex.isInfected():
                    if VERBOSE:
                        print(vertex.name, "unchanged, already infected")
                    continue
                vertex.infectVertex(currentDate)
                if vertex.isInfected():
                    justInfected.append(vertex)
                if VERBOSE:
                    if vertex.isInfected():
                        print(vertex.name, "infected")
                    else:
                        print(vertex.name, "lost virginity")
        if VERBOSE:
            print(".")
            print("Infected afterhand:")
            print([x.name for x in WetClique.allVertices.values() if x.isInfected()])
            print("~~~~~")
        
        return justInfected

    def B2_LogInfections(self, justInfected, currentDate):
        
        # 2. log ONLY transmissions
        # note: creation and destruction deferred to 5, to await complete information

        if PROGRESS_SUBCHECK: print("B. log transmissions")

        vertex: WetClique
        for vertex in justInfected:
            workingTuple = vertex.riskCounts.getState()

            if VERBOSE:
                print(vertex.name, "workingTuple is", workingTuple)
                
            if vertex.infectedBefore(currentDate): assert False

            self.probSeparator.add(vertex.name, workingTuple, True, 1)
            
            # cancel out a non-transmission for one timestep 
            self.probSeparator.add(vertex.name, workingTuple, False, -1)
            
            if VERBOSE:
                print(vertex.name, "from", vertex.riskLastChanged, "(", 1, "timesteps", "),", True)
                print("   ", vertex.riskCounts.internalList)
                
        if VERBOSE:
            print("~~~~~")
            
    def B3_Recover(self, probRecovery, currentDate) -> list[WetClique]:
        
        # 3. remove infections
        
        justRecovered: list = list()
        
        if probRecovery != 0:

            if PROGRESS_SUBCHECK: print("C. remove infections")
            if VERBOSE:
                print("Infected beforehand:")
                print([x.name for x in WetClique.allVertices.values() if x.isInfected()])
                print(".")

            vertex: WetClique
            for vertex in (WetClique.infectedVertices):
                # a vertex cannot be infected and recovered in the same timestep
                if not vertex.infectedBefore(currentDate): continue
            
                if random.random() < probRecovery:
                    # recover
                    justRecovered.append(vertex)
                    if VERBOSE: print(vertex.name, "recovered")
                else:
                    # don't recover
                    if VERBOSE: print(vertex.name, "not recovered")
                   
            # to avoid broken for loop, recover all vertices simultaneously
            vertex: WetClique        
            for vertex in justRecovered:
                vertex.recoverVertex(currentDate)
        
            if VERBOSE:
                print(".")
                print("Infected afterhand:")
                print([x.name for x in WetClique.allVertices.values() if x.isInfected()])
                print("~~~~~")
                
        return justRecovered
    
    def B4_LogExistence(self, justToggled, currentDate) -> None:
        
        # 4. log creation and destruction
        
        if PROGRESS_SUBCHECK: print("D. log creation and destruction")
            
        changedCliques: set = set()
        
        # collect all unique cliques that must be updated
        # 
        
        vertex: WetClique
        isolatedVertices = list()
        for vertex in justToggled:
            if not vertex.inCliques:
                isolatedVertices.append(vertex)
            clique: WetClique
            for clique in vertex.inCliques:
                changedCliques.add(clique)

        self.ApplyDeltas(changedCliques, True, currentDate, isolatedVertices = isolatedVertices)
            
        if VERBOSE: print("~~~~~")
        
    def B5_AddCliques(self, week, currentDate) -> CountList:
        # 5. populate cliques
        if PROGRESS_SUBCHECK: print("E. populate cliques")
        
        addedCliques: set = set()
        
        # collect all unique cliques that must be updated
        row: dict
        for row in week:
            ids = [x["UID"] for x in row["accusation"]]
        
            if VERBOSE: print(row["complaint"]["cr_id"], row["complaint"]["incident_date"])
            if VERBOSE: print(ids)
    
            vertices = set([WetClique.allVertices[x] for x in ids])
        
            output = WetClique.update(vertices, currentDate)
            
            if MODEL_NAME() == "pure":
                vertex: WetClique
                for vertex in vertices:
                    self.probSeparator.add(vertex.name, vertex.name, -1)
            
            if VERBOSE:
                vertex: WetClique
                for vertex in WetClique.allVertices.values():
                    print("vertex", vertex.name, "risk counts:")
                    print("   ", vertex.riskCounts.getState())
            
            addedCliques.update(output)
            
        if MODEL_NAME() in {"baseline", "hypergraph"}:
            self.ApplyDeltas(addedCliques, False, currentDate)
            
        if VERBOSE: print("~~~~~")
        
    def Z1_FinishVertices(self, currentDate) -> None:
        
        if VERBOSE:
            print("Z: finish all vertices")
        
        if MODEL_NAME() in {"baseline", "hypergraph"}:
            vertex: WetClique
            for vertex in WetClique.allVertices.values():
                if vertex.infectedBefore(currentDate): continue
        
                if not vertex.virginity:
                    weight: int = (currentDate - vertex.riskLastChanged) // DATE_RES
                    self.probSeparator.add(vertex.name, vertex.riskCounts.getState(), False, weight)
            
                    if VERBOSE and weight != 0:
                        print(vertex.name, "from", vertex.riskLastChanged, "(", weight, "timesteps", "),", False)
                        print("   ", vertex.riskCounts.getState())
        if MODEL_NAME() == "pure":
            clique: WetClique
            for clique in WetClique.allCliques.values():
                for size in SIZE_RANGE():
                    #numFaces = math.comb(clique.cliqueSize, size) * clique.coef
                    numFaces = math.comb(clique.cliqueSize - 1, size - 1) * clique.coef
                    vertex: WetClique
                    for vertex in clique.vertices:
                        self.probSeparator.add(vertex.name, vertex.name, size, numFaces)
            vertex: WetClique
            for vertex in WetClique.allVertices.values():
                self.probSeparator.add(vertex.name, vertex.name, -1, 0)
                
    def Z2_MidData(self, probRecovery) -> None:
        midFilename = MID_DATA_PREFIX + OUTPUT_FILENAME()
        dotLoc = midFilename.find(".")
        midFilename = midFilename[:dotLoc] + "_" + MODEL_NAME() + "_" + str(probRecovery) + ".csv"
        
        with open(midFilename, "w", newline = "\n") as midFile:
            if MODEL_NAME() == "pure":
                fieldnames = list(SIZE_RANGE()) + [-1]
                writer = csv.DictWriter(midFile, fieldnames=fieldnames, restval=0)
            
                writer.writeheader()
            
                for sample in self.probSeparator.trainDataCollector.probTable.internalDict.values():
                    writer.writerow(sample)
            if MODEL_NAME() == "baseline":
                fieldnames = list(SIZE_RANGE()) + [True, False]
                writer = csv.DictWriter(midFile, fieldnames=fieldnames, restval=0)
            
                writer.writeheader()
            
                for sample in self.probSeparator.trainDataCollector.probTable.internalDict.items():
                    row = sample[0].internalDict | sample[1]
                    writer.writerow(row)
            if MODEL_NAME() == "hypergraph":
                fieldnames = list()
                rows = list()
                
                for sample in self.probSeparator.trainDataCollector.probTable.internalDict.items():
                    row = sample[0].internalDict | sample[1]
                    fieldnames += [str(key) for key in row.keys() if key not in rows and isinstance(key, Fraction)]
                    
                    row = {str(key) if isinstance(key, Fraction) else key: value for key,value in row.items()}
                    rows.append(row)
                    
                fieldnames.sort()
                fieldnames += [True, False]
                    
                writer = csv.DictWriter(midFile, fieldnames=fieldnames, restval=0)
                writer.writeheader
                writer.writerows(rows)
                    
    def Z3_RegressData(self) -> None:
        # print(self.probSeparator.trainDataCollector.probTable.internalDict)

        if MODEL_NAME() in {"baseline", "pure"}:
            self.probSeparator.regress(verbose=True)
        if MODEL_NAME() in {"hypergraph"}:
            # add 2 to THETA_COUNT and remove the endpoints manually
            bigTheta: float
            for bigTheta in linspace(0,1,THETA_COUNT()+2):
                if not bigTheta.is_integer():
                    self.probSeparator.regress(verbose=True, bigTheta=bigTheta)
                    
    def TESTONLY_AnalyzeGraph(self) -> None:
        G = nx.Graph()
        
        vertex: WetClique
        for vertex in WetClique.allVertices.values():
            if len(vertex.adjVertices) > 0:
                G.add_node(vertex)
        for vertex in WetClique.allVertices.values():
            for adjVertex in vertex.adjVertices:
                if vertex.name > adjVertex.name: continue
                G.add_edge(vertex, adjVertex)
                
        largest_cc: nx.Graph = max(nx.connected_components(G), key=len)
                
        print("TESTONLY")
        print(G.number_of_nodes())
        print(G.number_of_edges())
        print(len(largest_cc))