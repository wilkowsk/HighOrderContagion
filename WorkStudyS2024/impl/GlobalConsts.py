from datetime import timedelta
import impl.GlobalConsts as GlobalConsts

__internalNonnegativity: bool = False
__internalFullDataset: bool = False
__internalOutputFilename: str = "zzzdefault.csv"
__internalModelName: str = "baseline"
__internalMaxCliqueSize: int = 3
__internalMuCount: int = 1
__internalThetaCount: int = 1

def NONNEGATIVITY(setVal: bool = None) -> bool:
    if setVal is not None:
        GlobalConsts.__internalNonnegativity = setVal
    return GlobalConsts.__internalNonnegativity

def FULL_DATASET(setVal: bool = None) -> bool:
    if setVal is not None:
        GlobalConsts.__internalFullDataset = setVal
    return GlobalConsts.__internalFullDataset

def OUTPUT_FILENAME(setVal: str = None) -> str:
    if setVal is not None:
        GlobalConsts.__internalOutputFilename = setVal
    return GlobalConsts.__internalOutputFilename

def MODEL_NAME(setVal: str = None) -> str:
    if setVal is not None:
        GlobalConsts.__internalModelName = setVal
    return GlobalConsts.__internalModelName

def MAX_CLIQUE_SIZE(setVal: int = None) -> int:
    if setVal is not None:
        GlobalConsts.__internalMaxCliqueSize = setVal
    return GlobalConsts.__internalMaxCliqueSize

def SIZE_RANGE() -> range:
    return range(2, MAX_CLIQUE_SIZE() + 1)

def MU_COUNT(setVal: float = None) -> float:
    if setVal is not None:
        GlobalConsts.__internalMuCount = setVal
    return GlobalConsts.__internalMuCount

def THETA_COUNT(setVal: float = None) -> float:
    if setVal is not None:
        GlobalConsts.__internalThetaCount = setVal
    return GlobalConsts.__internalThetaCount

DATE_MIN = "0001-01-01"
DATE_INITIAL = "1990-01-01"
#DATE_INITIAL = "1991-02-18" # to avoid a massive clique on the week of 1991-02-18
DATE_FINAL = "2020-01-01" # TODO: check this value
DATE_MAX = "9999-12-31"

MID_DATA_PREFIX = "mid-data/"
CPDP_DATA_PREFIX = "cpdp-data/"
RAND_DATA_PREFIX = "rand-data/"
OUTPUT_DATA_PREFIX = "output-data/"

PROFILE_FILENAME = "final-profiles.csv"
ACCUSED_FILENAME = "complaints-accused.csv"
COMPLAINTS_FILENAME = "complaints-complaints.csv"

VERBOSE = False
PROGRESS_CHECK = False
PROGRESS_SUBCHECK = False

FETCHER_TYPE = "offense"

INT_RES = 7
DATE_RES = timedelta(days = INT_RES)

ALL_MODELS = {
    "b": "baseline",
    "h": "hypergraph",
    "p": "pure"
}
"""
DATE_MIN = "0001-01-01"
DATE_INITIAL = "1990-01-01"
#DATE_INITIAL = "1991-02-18" # to avoid a massive clique on the week of 1991-02-18
DATE_FINAL = "2020-01-01" # TODO: check this value
DATE_MAX = "9999-12-31"

MID_DATA_PREFIX = "mid-data/"
CPDP_DATA_PREFIX = "cpdp-data/"
RAND_DATA_PREFIX = "rand-data/"
OUTPUT_DATA_PREFIX = "output-data/"

PROFILE_FILENAME = "final-profiles.csv"
ACCUSED_FILENAME = "complaints-accused.csv"
COMPLAINTS_FILENAME = "complaints-complaints.csv"

VERBOSE = True
PROGRESS_CHECK = False
PROGRESS_SUBCHECK = False

#FETCHER_TYPE = "offense"
FETCHER_TYPE = "random"

#INT_RES = 7
INT_RES = 1
DATE_RES = timedelta(days = INT_RES)

ALL_MODELS = {
    "b": "baseline",
    "h": "hypergraph",
    "p": "pure"
}
"""