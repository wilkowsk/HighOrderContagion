import csv
import os

import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib.axes import Axes
import numpy
import impl.WetAnalysis as WetAnalysis
from impl.GlobalConsts import *
from impl.OffenseFetcher import OffenseFetcher
from impl.RandomFetcher import RandomFetcher
from numpy import linspace

import statsmodels.api as sm

def WetSpectrum():
    if FULL_DATASET():
        profileCond = lambda row: True
    else:
        profileCond = lambda row: row["UID"][-1] == "5"
        
    if FETCHER_TYPE == "random":
        fetcher = RandomFetcher(8,6,24)
    else:
        fetcher = OffenseFetcher(PROFILE_FILENAME, ACCUSED_FILENAME, COMPLAINTS_FILENAME, profileCond = profileCond)
    
    # obtain evenly spaced tests over the interval [0,1]
    for prob in linspace(0, 1, MU_COUNT()):
        print("Recovery probability:", prob)
        WetAnalysis.tabulate(fetcher, prob)
        print()
        
def SpectrumGraph(filename: str = None):
    if filename is None:
        filename = OUTPUT_FILENAME()
    filename = OUTPUT_DATA_PREFIX + filename
    
    font = {"family": "Arial",
            "size": "8"}
            
    mpl.rc("font", **font)
    mpl.rcParams['axes.linewidth'] = 2.36220472 * 0.24
    mpl.rcParams['xtick.major.width'] = 2.36220472 * 0.24
    mpl.rcParams['ytick.major.width'] = 2.36220472 * 0.24

    modelName: str = DeduceModel(filename)

    match modelName:
        
        case "baseline":
    
            mus: list = list()
            scores: list = list()
            betas: list = list()
            crossScores: list = list()
    
            with open(filename, newline="") as dataSource:
                fieldnames = ""
                dataCsv = csv.DictReader(dataSource)
                for betaIndex in range(CountBetas(dataCsv.fieldnames)):
                    betas.append(list())

                for row in dataCsv:
                    mus.append(float(row["mu"]))
                    scores.append(float(row["score"]))
                    for subscript in range(len(betas)):
                        betas[subscript].append(float(row["beta_" + str(subscript)]))
                    crossScores.append(float(row["cross-score"]))
            
            fig, (ax1, ax2) = plt.subplots(1,2,layout="constrained")
            ax1.scatter(mus, scores)
            ax1.set_xlabel("Probability of recovery (μ)")
            ax1.set_ylabel("Linear regression score")
    
            for subscript in range(len(betas)):
                ax2.scatter(mus, betas[subscript], label="β_" + str(subscript))
            ax2.set_xlabel("Probability of recovery (μ)")
            ax2.set_ylabel("Parameter value")
            ax2.legend()

            fig.set_figwidth(5.2)
            fig.set_figheight(3.5)
            fig.set_dpi(300)

            fig.savefig("figures/" + OUTPUT_FILENAME().removesuffix(".csv") + "_1.tiff", dpi=300, format="tiff")
            plt.show()
            
        case "pure":
            
            with open(filename, newline="") as dataSource:
                print(dataSource.read())
                
        case "hypergraph":

            deltas: list = list()
            thetas: list = list()
            scores: list = list()
            lambdas: list = list()
            crossScores: list = list()
            
            with open(filename, newline="") as dataSource:
                fieldnames = ""
                dataCsv = csv.DictReader(dataSource)
                for betaIndex in range(3):
                    lambdas.append(list())

                for row in dataCsv:
                    if not float(row["delta_I"]) in deltas:
                        deltas.append(float(row["delta_I"]))
                    if not float(row["theta'_J"]) in thetas:
                        thetas.append(float(row["theta'_J"]))
                    scores.append(float(row["score"]))
                    lambdas[0].append(float(row["lambda_I"]))
                    lambdas[1].append(float(row["lambda_J<"]))
                    lambdas[2].append(float(row["lambda_J>="]))
                    crossScores.append(float(row["cross-score"]))
                    
            # convert lambdas to np list
            
            scores: numpy.ndarray = numpy.array(scores)
            scores = scores.reshape(len(deltas), len(thetas))
            
            cmap = plt.colormaps["RdBu"]
            fig, ax = plt.subplots(1,1,layout="constrained")
            maxMagnitude = numpy.max(numpy.abs(scores))
            norm = colors.Normalize(vmin=-maxMagnitude, vmax=maxMagnitude)
            
            ax.pcolormesh(thetas, deltas, scores, shading="nearest", cmap=cmap, norm=norm)

            ax.set_xlabel("Infection threshold (Θ'_J)")
            ax.set_ylabel("Probability of recovery (δ_I)")

            ax.set_title("Coefficient of determination (R^2)")
            
            fig.colorbar(None, ax=ax, orientation="vertical", fraction = 0.1, cmap=cmap, norm=norm)
            
            fig.set_figwidth(5.2)
            fig.set_figheight(3.5)
            fig.set_dpi(300)
            
            fig.savefig("figures/" + OUTPUT_FILENAME().removesuffix(".csv") + "_1.tiff", dpi=300, format="tiff")
            plt.show()

            # ---------
            
            lambdas: numpy.ndarray = numpy.array(lambdas)
            lambdas = lambdas.reshape(3, len(deltas), len(thetas))
                    
            fig, axs = plt.subplots(1,3,layout="constrained")
            
            cmap = plt.colormaps["RdBu"]
            maxMagnitude = numpy.max(numpy.abs(lambdas))
            #norm = colors.Normalize(vmin=-maxMagnitude, vmax=maxMagnitude)
            norm = colors.Normalize(vmin=-.008, vmax=.008)
            
            for subscript in range(3):
                axs[subscript].pcolormesh(thetas, deltas, lambdas[subscript], shading="nearest", cmap=cmap, norm=norm)
                
            for ax in axs:
                ax.set_xlabel("Infection threshold (Θ'_J)")
                ax.set_ylabel("Probability of recovery (δ_I)")
                
            axs[0].set_title("Constant term (λ_I)")
            axs[1].set_title("Below-Threshold term (λ_J,<)")
            axs[2].set_title("Above-Threshold term (λ_J,>=)")
                
            fig.colorbar(None, ax=axs, orientation='vertical', fraction=0.1, cmap=cmap, norm=norm)
            
            fig.set_figwidth(7.5)
            fig.set_figheight(3.5)
            fig.set_dpi(300)
            
            fig.savefig("figures/" + OUTPUT_FILENAME().removesuffix(".csv") + "_2.tiff", dpi=300, format="tiff")
            plt.show()
        
        case _:
            
            print("Unrecognized file")
    
    
def CountBetas(fieldnames) -> int:
    output: int = 0
    while True:
        if "beta_" + str(output) in fieldnames:
            output += 1
        else:
            return output
                    
def DeduceModel(outputFilename: str) -> str:
    _, suffix = os.path.splitext(outputFilename)
    
    match suffix:
        case ".txt":
            return "pure"
        case ".csv":
            with open(outputFilename, newline="") as dataSource:
                dataCsv = csv.DictReader(dataSource)
                if "delta_I" in dataCsv.fieldnames:
                    return "hypergraph"
                elif "mu" in dataCsv.fieldnames:
                    return "baseline"
                else:
                    assert False