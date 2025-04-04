import unittest

import itertools
from impl.OffenseFetcher import OffenseFetcher
from impl.ImplyClique import ImplyClique
import random
import numpy
import math
import networkx as nx

from impl.WetClique import WetClique

class Test_test_correctness(unittest.TestCase):
    def test_count(self):
        numTests:       int = 64
        numVertices:    int = 64
        numCliques:     int = 64

        enableTheirs:  bool = True

        rng = numpy.random.default_rng()

        for iterationCount in range(numTests):
            ImplyClique.reset()
    
            if (enableTheirs):
                theirGraph = nx.Graph()
    
            for letter in range(numVertices):
                name: str = "V" + str(letter)
        
                # OUR IMPL.
                v = ImplyClique(name=name)
        
                # THEIR IMPL.
                if (enableTheirs):
                    theirGraph.add_node(name)
    
            for cliqueNum in range(numCliques):
        
                cliqueSize = rng.binomial(numVertices, 3/numVertices)   # TODO: find a better distribution
                indices = random.sample(range(numVertices), cliqueSize)
                """
            for indices in itertools.combinations(range(0,3), 2):
                cliqueNum = 0    
                """
                names = ["V" + str(x) for x in indices]
        
                nilpadCliqueNum = "0" * (math.ceil(math.log10(numCliques)) - len(str(cliqueNum))) + str(cliqueNum)
                nilpadIterationCount = "0" * (math.ceil(math.log10(numTests)) - len(str(iterationCount))) + str(iterationCount)
                print(nilpadIterationCount, nilpadCliqueNum, names)
        
                # OUR IMPL.
                vertices = set([ImplyClique.allVertices.get(x) for x in names])
                ImplyClique.update(vertices)
        
                # THEIR IMPL.
                if (enableTheirs):
                    for x, y in itertools.combinations(names, 2):
                        theirGraph.add_edge(x, y)
                    theirCliques = list(nx.find_cliques(theirGraph))
        
        
                """
                print("~~~~~")
        
                for v in ImplyClique.allVertices.values():
                    if str(v):
                        print(v)
                
                for v in ImplyClique.maxCliques.values():
                    if str(v):
                        print(v)
                
                print("~~~~~")
                """
        
                ImplyClique.sanityCheck()
        
                if (enableTheirs):
                    assert len(theirCliques) == len(ImplyClique.maxCliques)
                    
    def test_wet(self):
        numTests:       int = 64
        numVertices:    int = 64
        numCliques:     int = 64

        enableTheirs:  bool = True

        rng = numpy.random.default_rng()

        for iterationCount in range(numTests):
            WetClique.reset()
    
            if (enableTheirs):
                theirGraph = nx.Graph()
                theirCliques = set()
    
            for letter in range(numVertices):
                name: str = "V" + str(letter)
        
                # OUR IMPL.
                v = WetClique(name=name)
        
                # THEIR IMPL.
                if (enableTheirs):
                    theirGraph.add_node(name)
                    theirCliques.add(tuple((name,)))
    
            for cliqueNum in range(numCliques):
        
                cliqueSize = rng.binomial(numVertices, 3/numVertices)   # TODO: find a better distribution
                indices = random.sample(range(numVertices), cliqueSize)
                """
            for indices in itertools.combinations(range(0,3), 2):
                cliqueNum = 0
                """
                names = ["V" + str(x) for x in indices]
        
                nilpadCliqueNum = "0" * (math.ceil(math.log10(numCliques)) - len(str(cliqueNum))) + str(cliqueNum)
                nilpadIterationCount = "0" * (math.ceil(math.log10(numTests)) - len(str(iterationCount))) + str(iterationCount)
                print(nilpadIterationCount, nilpadCliqueNum, names)
        
                # OUR IMPL.
                vertices = set([WetClique.allVertices.get(x) for x in names])
                WetClique.update(vertices)
        
                # THEIR IMPL.
                if (enableTheirs):
                    for x, y in itertools.combinations(names, 2):
                        theirGraph.add_edge(x, y)
                        
                    # NOTE: This code adapted from https://stackoverflow.com/questions/58775867/what-is-the-best-way-to-count-the-cliques-of-size-k-in-an-undirected-graph-using
                    for k in range(1, WetClique.maxSize + 1):
                        if len(names) == k:
                            theirCliques.add(tuple(sorted(names)))
                        elif len(names) > k:
                            for mini_clique in itertools.combinations(names, k):
                                theirCliques.add(tuple(sorted(mini_clique)))
        
        
                """
                print("~~~~~")
        
                for v in ImplyClique.allVertices.values():
                    if str(v):
                        print(v)
                
                for v in ImplyClique.maxCliques.values():
                    if str(v):
                        print(v)
                
                print("~~~~~")
                """
        
                WetClique.sanityCheck()
                
                print(len(theirCliques))
                print(len(WetClique.allCliques))
        
                if (enableTheirs):
                    assert len(theirCliques) == len(WetClique.allCliques)

if __name__ == '__main__':
    unittest.main()