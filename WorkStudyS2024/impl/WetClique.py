from bisect import bisect_left
from fractions import Fraction
import functools
import itertools
import math
from datetime import date
from impl.CountCollections import CountDict, CountList
from impl.GlobalConsts import *
from impl.RiskCounts import RiskCounts

class WetClique:
    
    allCliques: dict = dict()    # keyed by a frozenset of the cliques' vertices
    allVertices: dict = dict()      # keyed by the vertex's name
    
    infectedVertices: set = set()
    
    idIterator: int = 0
    
    # initialize the clique with the given set of vertices and the given name.
    # the clique becomes a vertex iff no vertices are supplied
    def __init__(self, name="", vertices=None, coef: int = 1, currentDate: date = date.fromisoformat(DATE_MIN)) -> None:
        
        self.internalId: int = type(self).idIterator
        type(self).idIterator += 1

        # if the new clique is not composed of vertices, then it is a vertex itself
        if (not vertices):
            self.name = name                # the name of this clique
            if (name == ""):
                self.name = "V" + str(len(type(self).allVertices))

            
            self.virginity: bool = True     # whether this vertex has a clean record (no complaints)
                                            # virgin vertices are immune to infection
            self.transDates: list[date] = list()
                                            # list of infection and recovery dates
            
            self.riskCounts: RiskCounts = RiskCounts()
                                            # count of cliques of size n endangering this vertex
            self.riskLastChanged: date = None
                                            # timestamp when riskDict was last changed
                                            
            self.adjVertices: set[WetClique] = set()
                                            # the set of vertices adjacent to this vertex
            self.inCliques: set[WetClique] = set()
                                            # all cliques this vertex is in

            self.logVertex()
            
        else:
            self.coef: int = coef
                                            # the multiplicity of this clique
            self.newlyAddedCoef: int = coef
                                            # the newly added multiplicity of this clique
            self.coefLastChanged: date = currentDate
                                            # timestamp when coef was last changed
            
            self.vertices: frozenset = frozenset(vertices)
                                            # the set of vertices this clique contains
            self.cliqueSize: int = len(self.vertices)
                                            # the size of this clique
            
            self.logClique()
            
    def addCoef(self, coef: int, currentDate: date) -> None:
        if currentDate > self.coefLastChanged:
            self.coefLastChanged = currentDate
            self.coef += coef
            self.newlyAddedCoef = coef
        else:
            self.coef += coef
            self.newlyAddedCoef += coef
        
    # returns true iff the vertex is currently infected
    def isInfected(self) -> bool:
        return self.infectedBefore(date.fromisoformat(DATE_MAX))

    # returns true iff the vertex was infected at the timestep before thresholdDate
    def infectedBefore(self, thresholdDate: date = date.fromisoformat(DATE_MAX)) -> bool:

        # this function calls only on vertices
        assert self in type(self).allVertices.values()
        
        # count a transition iff its date is strictly less than thresholdDate
        numTransitions: int = bisect_left(self.transDates, thresholdDate)
        output: bool = numTransitions % 2 == 1
        return output
    
    def endangerDict(self, thresholdDate: date = date.fromisoformat(DATE_MAX), hasFormer: bool = True) -> dict[CountList]:
    
        # this function calls only on cliques
        assert self in type(self).allCliques.values()
        
        numInfected: int = len([x for x in self.vertices if x.infectedBefore(thresholdDate)])
        output: dict[CountList] = dict()
        workingCoef: int = (self.coef if hasFormer else self.newlyAddedCoef)
        
        # precompute the risk for uninfected vertices
        
        uninfectedRisk: CountList = CountList()
        if MODEL_NAME() in {"baseline", "pure"}:
            for size in SIZE_RANGE():
                # need size-1 infected vertices
                numVectors: int = math.comb(numInfected, size-1)
                # adjust by clique's coefficient
                numVectors *= workingCoef
            
                uninfectedRisk.add(size, numVectors)
        if MODEL_NAME() == "hypergraph":
            uninfectedRisk.add(Fraction(numInfected, self.cliqueSize), workingCoef)
            
        # precompute the dict for infected vertices
            
        infectedRisk: CountList = CountList()
        if MODEL_NAME() == "hypergraph":
            infectedRisk.add(Fraction(), workingCoef)
        
        vertex: "WetClique"
        for vertex in self.vertices:
            if not vertex.infectedBefore(thresholdDate):
                output[vertex] = uninfectedRisk
            else:
                output[vertex] = infectedRisk

        return output
                        
    
    def infectVertex(self, currentDate: date) -> None:

        # this function calls only on vertices
        assert self in type(self).allVertices.values()
        
        if self.virginity:              # virgin vertices are immune to infection
            self.virginity = False      # but they lose their virginity in the process
            self.riskLastChanged = currentDate
            return
        if self.isInfected():
            return                      # cannot doubly infect a vertex
        
        self.transDates.append(currentDate)
        type(self).infectedVertices.add(self)

    def recoverVertex(self, currentDate: date) -> None:

        # this function calls only on vertices
        assert self in type(self).allVertices.values()
        
        if not self.isInfected:
            return                      # cannot doubly recover a vertex
        
        self.transDates.append(currentDate)
        type(self).infectedVertices.remove(self)
    
    # adds clique to dict "allCliques", etc
    def logClique(self) -> None:
        type(self).allCliques[self.vertices] = self
        # self.updateVectorStatus()
        
    # adds vertex to dict "allVertices", etc
    def logVertex(self) -> None:
        assert self.name not in type(self).allVertices.keys()
        type(self).allVertices[self.name] = self

    # resets all global variables
    @classmethod
    def reset(cls) -> None:
        cls.allCliques = dict()
        cls.allVertices = dict()
        cls.infectedVertices = set()
        cls.idIterator = 0      # to prevent overflow

    # makes clique using vertices, ensuring that the vertices have consistent state
    @classmethod
    def joinVertices(cls, vertices: set["WetClique"], currentDate: date, coef: int = 1) -> "WetClique":
        if len(vertices) <= 1: return None

        if (frozenset(vertices) in cls.allCliques.keys()):
            # we have already logged this clique
            # add our coefficient to its own
            redundantClique: cls = cls.allCliques[frozenset(vertices)]
            redundantClique.addCoef(coef, currentDate)
            return redundantClique
        
        output: WetClique = WetClique(vertices=vertices, coef=coef, currentDate=currentDate)
        
        vertex: WetClique
        for vertex in vertices:
            vertex.inCliques.add(output)
            
            # log each other vertex as adjacent to this one
            #assert vertex in cls.allVertices.values()
            vertex.adjVertices |= (vertices - {vertex})
            
        return output
    
    # makes clique using vertices, ensuring that all structures have consistent state
    @classmethod
    def update(cls, vertices: set, currentDate: date) -> set:
        output = set()

        workingCliques = set()
        for vertex in vertices:
            workingCliques |= vertex.inCliques
            
        if MODEL_NAME() in {"baseline", "pure"}:
            # cancel out all intersections with our clique
            # to avoid conflict, handle cliques in order from smallest to largest    
            for clique in sorted(workingCliques, key = lambda x: x.cliqueSize):
                # coef changes during the execution of this method
                # calculate the old value from our logs

                commonVertices = vertices & clique.vertices
                addendClique = cls.joinVertices(commonVertices, currentDate, -1 * clique.coef)
                if addendClique: output.add(addendClique)
            
        # add the clique
        addendClique = cls.joinVertices(vertices, currentDate)
        if addendClique: output.add(addendClique)
    
        return output
            
    def __str__(self) -> str:
        if (self in type(self).allVertices.values() and not self.adjVertices): return ""

        output = ""
        subOutput = ""
        if (self in type(self).allVertices.values()):
            output += "Vertex " + self.name + ":\n"
            output += "Adjacent to vertices:\n"
            for vertex in sorted(self.adjVertices, key=lambda x: x.name):
                subOutput += ", " if subOutput else ""
                subOutput += vertex.name
        else:
            output += "Clique of order " + str(self.cliqueSize) + ":\n"
            output += "Has multiplicity " + str(self.coef) + "\n"
            output += "Added mult " + str(self.newlyAddedCoef) + " as of " + str(self.coefLastChanged) + "\n"
            output += "Contains vertices:\n"
            for vertex in sorted(self.vertices, key=lambda x: x.name):
                subOutput += ", " if subOutput else ""
                subOutput += vertex.name
                
        subOutput = subOutput if subOutput else "(none)"
        output += subOutput + "\n"
        return output
                    
    def shortStr(self) -> str:
        if (self.cliqueSize == 1 and not self.adjVertices): return ""
        
        subOutput = ""
        for vertex in self.vertices:
            subOutput += ", " if subOutput else ""
            subOutput += vertex.name
            
        subOutput = subOutput if subOutput else "(none)"
        output = "(" + subOutput + ")"
        return output