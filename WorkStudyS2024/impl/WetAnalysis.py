from impl.WetClique import WetClique
from impl.WetSteps import WetSteps
from impl.CountCollections import CountList

from datetime import date

from impl.GlobalConsts import *

class WetAnalysis:
    @classmethod
    def beforeLoop(cls, ws):
        pass
    
    # override this method in subclasses if necessary
    @classmethod
    def atLoopBegin(cls, week):
        pass
    
    # override this method in subclasses if necessary
    @classmethod
    def atLoopEnd(cls, week):
        pass

    @classmethod
    def tabulate(cls, fetcher, probRecovery: float = 0,
                 *, profileCond = lambda x: True, doRegress = True):
    
        ws = WetSteps()
    
        weeklyList: list = ws.A_Init(fetcher, probRecovery)
        
        cls.beforeLoop(ws)
    
        # timesteps
    
        currentDate = date.fromisoformat(DATE_INITIAL)

        for week in weeklyList:
        
            # if PROGRESS_CHECK: print(currentDate)

            cls.atLoopBegin(week)
        
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
                justInfected: list = ws.B1_Infect(week, currentDate)
        
                ws.B2_LogInfections(justInfected, currentDate)
        
                justRecovered: list = ws.B3_Recover(probRecovery, currentDate)
        
                ws.B4_LogExistence(justInfected+justRecovered, currentDate)

            ws.B5_AddCliques(week, currentDate)
        
            # 6. display internal state
            # if VERBOSE:
            #     for vertex in WetClique.allVertices.values():
            #         vertexString = str(vertex)
            #         if vertexString:
            #             print(vertexString)
            
            #     for clique in WetClique.allCliques.values():
            #         print(clique)
            
            cls.atLoopEnd(week)

            # Z. end loop
            currentDate += DATE_RES
        
        # currentDate overstepped its bounds. bring it back
        currentDate -= DATE_RES
        
        ws.Z1_FinishVertices(currentDate)
        
        ws.Z2_MidData(probRecovery)
    
        #ws.TESTONLY_AnalyzeGraph()
    
        if doRegress:
            ws.Z3_RegressData()
    
    