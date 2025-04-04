import impl.WetAnalysis as WetAnalysis
from impl.OffenseFetcher import *
from impl.MimicFetcher import *
from impl.RandomFetcher import *

import src.WetMain as WetMain

import impl.GlobalConsts as GlobalConsts

profileFilename = GlobalConsts.PROFILE_FILENAME
accusedFilename = GlobalConsts.ACCUSED_FILENAME
complaintsFilename = GlobalConsts.COMPLAINTS_FILENAME

import src.IOMiddleman as IOMiddleman

# the following is a test. when not in use, change to "if False"

if False:
    GlobalConsts.VERBOSE = True
    print(GlobalConsts.VERBOSE)
    GlobalConsts.OUTPUT_FILENAME("zzzdefault.txt")
    GlobalConsts.NONNEGATIVITY(False)
    GlobalConsts.FULL_DATASET(False)
    GlobalConsts.MODEL_NAME("pure")
    GlobalConsts.MAX_CLIQUE_SIZE(2)
    WetMain.WetSpectrum()
    exit()

violentCodes = {"03E", "03S", "05A", "05B", "05C", "05D", "05E", "05F", "05G", "05H", "05J", "05M", "05N", "05P", "05Q", "05R", "05T", "05Z",
                "05ZZA", "05ZZB", "05ZZC", "05ZZD", "05ZZE", "05ZZL", "05ZZM", "18B", "19A", "19B", "19Z", "20A",
                "S001", "S002", "S005", "S006", "S007", "S008", "S009", "S010", "S011", "S014", "S020", "S021", "S022", "S023", "S025", "S026", "S028", "S029",
                "S030", "S031", "S034", "S035", "S042", "S043", "S044", "S051", "S058", "S065", "S083", "S085", "S093", "S094", "S101", "S109",
                "S110", "S117", "S118", "S121", "S125", "S126", "S249", "S251", "S253"}

result = IOMiddleman.Initialize()

if result:
    WetMain.WetSpectrum()
    
WetMain.SpectrumGraph()