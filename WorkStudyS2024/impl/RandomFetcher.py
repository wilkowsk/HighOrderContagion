import csv
import random
from datetime import date, timedelta
from impl.GlobalConsts import *

class RandomFetcher:
    
    def __init__(self, numVertices: int, numCliques: int, numOffenses: int):
        self.numVertices: int = numVertices
        self.numCliques: int = numCliques
        self.numOffenses: int = numOffenses

        # safeguard
        if self.numOffenses > self.numVertices * self.numCliques:
            self.numOffenses = self.numVertices * self.numCliques

    # returns a dict of profiles, keyed by UID
    def getProfileDict(self) -> dict[str, dict[str, str]]:
        profileDict: dict[str, dict[str, str]] = dict()
    
        # cols: UID
        #       first_name	    last_name	    middle_initial	middle_initial2
        #       suffix_name	    birth_year	    race	        gender
        #       appointed_date	resignation_date	            current_status
        #       current_star	current_unit	current_rank	start_date
        #       org_hire_date	profile_count	cleaned_rank	link_UID

        for number in range(self.numVertices):
            uid = "V" + str(number)
            row: dict[str, str] = {
                "UID": uid,
                "appointed_date": date.isoformat(date.fromisoformat(DATE_MIN) + timedelta(number)),
                "resignation_date": date.isoformat(date.fromisoformat(DATE_INITIAL) + timedelta(self.numCliques)),
            }
            profileDict[row["UID"]] = row

        with open(RAND_DATA_PREFIX + PROFILE_FILENAME, "w", newline="") as profileDataFile:
            fieldnames = ["UID", "appointed_date", "resignation_date"]
            writer = csv.DictWriter(profileDataFile, fieldnames=fieldnames)
    
            writer.writeheader()
            for entry in profileDict.values():
                writer.writerow(entry)
        return profileDict
    
    # returns a list of complaints
    # each complaint is a dict consisting of an [accusation] and a [complaint] part
    def getComplaintList(self, profileDict: dict) -> list[dict[str]]:
        
        accusationDict: dict[str, list[dict[str, str]]] = dict()
        
        # [accusation]
        # cols: cr_id
        #       UID	            complaint_category	            complaint_code
        #       cv	            final_finding	final_outcome	recc_finding	
        #       recc_outcome	link_UID
        
        for number in range(self.numOffenses):
            isValid = False;
            
            crid: str = ""
            while (not isValid):
                crid = "Q" + str(random.randint(0, self.numCliques-1))
                row: dict[str, str] = {
                    "cr_id": crid,
                    "UID": "V" + str(random.randint(0, self.numVertices-1))
                }
                if row not in accusationDict.get(row["cr_id"], []):
                    isValid = True;
            
            if crid not in accusationDict:
                accusationDict[crid] = list()
            accusationDict[row["cr_id"]].append(row)
            
        with open(RAND_DATA_PREFIX + ACCUSED_FILENAME, "w", newline="") as accusedDataFile:
            fieldnames = ["cr_id", "UID"]
            writer = csv.DictWriter(accusedDataFile, fieldnames=fieldnames)
    
            writer.writeheader()
            rows: list[dict[str, str]]
            for rows in accusationDict.values():
                entry: dict[str, str]
                for entry in rows:
                    writer.writerow(entry)


        complaintList: list[dict[str, str]] = list()
        
        # [complaint]
        # cols: cr_id
        #       cv	            incident_date	complaint_date	closed_date
        #      	add1	        add2	        beat	        city
        #      	full_address	location
            
        for number in range(self.numCliques):
            crid: str = "Q" + str(number)
            incidentDate: str = date.isoformat(date.fromisoformat(DATE_INITIAL) + timedelta(number))
            
            row: dict[str, str] = {
                "cr_id": crid,
                "incident_date": incidentDate
            }
                
            complaintList.append(row)

        with open(RAND_DATA_PREFIX + COMPLAINTS_FILENAME, "w", newline="") as complaintsDataFile:
            fieldnames = ["cr_id", "incident_date"]
            writer = csv.DictWriter(complaintsDataFile, fieldnames=fieldnames)
    
            writer.writeheader()
            entry: dict[str, str]
            for entry in complaintList:
                writer.writerow(entry)
            
        # sort by incident date
        complaintList.sort(key=lambda row: row["incident_date"])
                
        output: list[dict[str]] = list()
        
        for row in complaintList:
            if row["cr_id"] not in accusationDict: continue
            outputEntry = {
                "complaint": row,
                "accusation": accusationDict[row["cr_id"]]
            }
            output.append(outputEntry)
        
        return output
    
    # returns a dict; keys are officer UIDs, values are the dates of all complaints in order
    # prerequisite: complaintList is sorted
    def allComplaintDates(self, complaintList: list[dict[str]]) -> dict:
        output = dict()
        
        currentDate: str = DATE_MIN
        
        row: dict[str]
        for row in complaintList:
            assert row["complaint"]["incident_date"] >= currentDate
            currentDate = row["complaint"]["incident_date"]

            accusee: dict[str, str]
            for accusee in row["accusation"]:
                output.setdefault(accusee["UID"], list())
                output[accusee["UID"]].append(currentDate)
        
        return output
            




