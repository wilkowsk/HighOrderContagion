from impl.WetClique import WetClique
from impl.WetSteps import WetSteps
from impl.CountCollections import CountList

from datetime import date

from impl.GlobalConsts import *

def tabulate(fetcher, probRecovery: float = 0,
             *, profileCond = lambda x: True):
    
    ws = WetSteps()
    
    weeklyList: list = ws.O_Init(fetcher, probRecovery)
    
    # timesteps
    
    currentDate = date.fromisoformat(DATE_INITIAL)

    for week in weeklyList:
        
        if PROGRESS_CHECK: print(currentDate)
        
        # proceed in order:
        
        # 0. show this timestep's cliques
        
        if VERBOSE:
            # print("0. show new cliques")
            for row in week:
                ids = [x["UID"] for x in row["accusation"]]
        
                print(row["complaint"]["cr_id"], row["complaint"]["incident_date"])
                print(ids)
            # print("~~~~~")

        if MODEL_NAME() in {"baseline", "hypergraph"}:
            justInfected: list = ws.I_Infect(week, currentDate)
        
            ws.II_LogInfections(justInfected, currentDate)
        
            justRecovered: list = ws.III_Recover(probRecovery, currentDate)
        
            ws.IV_LogExistence(justInfected+justRecovered, currentDate)

        ws.V_AddCliques(week, currentDate)
        
        # 6. display internal state
        if VERBOSE:
            for vertex in WetClique.allVertices.values():
                vertexString = str(vertex)
                if vertexString:
                    print(vertexString)
            
            for clique in WetClique.allCliques.values():
                print(clique)

        # Z. end loop
        currentDate += DATE_RES
        
    # currentDate overstepped its bounds. bring it back
    currentDate -= DATE_RES
        
    ws.Z_FinishVertices(currentDate)
    
    #ws.TESTONLY_AnalyzeGraph()
    
    ws.Z_RegressData()
    
    