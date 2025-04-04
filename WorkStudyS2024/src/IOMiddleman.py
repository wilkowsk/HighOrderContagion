import csv
import glob
import os
from impl.GlobalConsts import *
import src.WetMain as WetMain

def Initialize():
    isGood: bool = False
    isGraphs: bool = False
    while not isGood:
        print("Enter output filename:")
        outputFilename: str = input("    ").lower()
        
        # remove file extension if present
        if "." in outputFilename:
            outputFilename = outputFilename[:outputFilename.find(".")]
            
        matchingFilenames: list = glob.glob(outputFilename + ".*", root_dir=OUTPUT_DATA_PREFIX)
        
        # if file already exists, req confirmation from user
        if matchingFilenames:
            print("File already exists. Enter action (Proceed / Cancel / Graphs):")
            confirm: str = input("    ").lower()
            if confirm.startswith("p"):
                isGood = True
            if confirm.startswith("g"):
                isGraphs = True
                isGood = True
                outputFilename = matchingFilenames[0]
        else:
            isGood = True
    OUTPUT_FILENAME(outputFilename)
    
    # if user selects "Graphs", immediately return False
    # main function calls SpectrumGraph automatically
    if isGraphs:
        return False
    
    isGood: bool = False
    while not isGood:
        print("Enter model name (Baseline / Pure / Hypergraph):")
        modelName: str = input("    ").lower()
        
        # if modelName is already valid, stop immediately
        if modelName in ALL_MODELS.values():
            isGood = True
            
        # otherwise, check each entry in ALL_MODELS
        else:
            for abbrev in ALL_MODELS.keys():
                if modelName.startswith(abbrev):
                    modelName = ALL_MODELS[abbrev]
                    isGood = True
                    break
        
        if not isGood:
            print("ERROR: Given model name was not recognized")
    MODEL_NAME(modelName)

    # add file extension to output filename
    suffix: str
    match MODEL_NAME():
        case "baseline" | "hypergraph":
            suffix = ".csv"
        case "pure":
            suffix = ".txt"
    OUTPUT_FILENAME(OUTPUT_FILENAME() + suffix)

    isGood: bool = False
    while not isGood:
        print("Enter dataset size (Partial / Full):")
        datasetStatus: str = input("    ").lower()
        
        if datasetStatus.startswith(("f")):
            datasetStatus = True
            isGood = True
        elif datasetStatus.startswith(("p")):
            datasetStatus = False
            isGood = True
        else:
            print("ERROR: Given dataset size was not recognized")
    FULL_DATASET(datasetStatus)
    
    if MODEL_NAME() in {"baseline", "pure"}:
        isGood: bool = False
        while not isGood:
            print("Enter maximum clique dimension:")
            try:
                maxCliqueSize: int = int(input("    "))
                if maxCliqueSize >= 1:
                    isGood = True
                else:
                    print("ERROR: Maximum clique dimension must be positive")
            except:
                print("ERROR: Maximum clique dimension must be an integer")
                
        # convert from dimension to vertex count
        maxCliqueSize += 1
        
        MAX_CLIQUE_SIZE(maxCliqueSize)
        
    if MODEL_NAME() in {"baseline", "pure", "hypergraph"}:
        isGood: bool = False
        while not isGood:
            print("Enter nonnegativity status (True / False / Yes / No):")
            datasetStatus: str = input("    ").lower()
        
            if datasetStatus.startswith(("t", "y")):
                datasetStatus = True
                isGood = True
            elif datasetStatus.startswith(("f", "n")):
                datasetStatus = False
                isGood = True
            else:
                print("ERROR: Nonnegativity status must be a boolean")
        NONNEGATIVITY(datasetStatus)
        
    if MODEL_NAME() in {"baseline", "hypergraph"}:
        isGood: bool = False
        while not isGood:
            varName = "mu" if MODEL_NAME() == "baseline" else "delta"
            print("Enter number of " + varName + " values to test:")
            try:
                muCount: int = int(input("    "))
                if muCount >= 1:
                    isGood = True
                else:
                    print("ERROR: Number of " + varName + " values must be positive")
            except:
                print("ERROR: Number of " + varName + " values must be an integer")
        MU_COUNT(muCount)
                
    if MODEL_NAME() == "hypergraph":
        isGood: bool = False
        while not isGood:
            print("Enter number of big theta values to test:")
            try:
                thetaCount: int = int(input("    "))
                if thetaCount >= 1:
                    isGood = True
                else:
                    print("ERROR: Number of big theta values must be positive")
            except:
                print("ERROR: Number of big theta values must be an integer")
        THETA_COUNT(thetaCount)
        
    return True