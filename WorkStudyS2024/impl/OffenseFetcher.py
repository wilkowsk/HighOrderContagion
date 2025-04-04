import csv

from impl.GlobalConsts import *

class OffenseFetcher:
    
    def __init__(self, profileFilename: str = PROFILE_FILENAME, accusedFilename: str = ACCUSED_FILENAME, complaintsFilename: str = COMPLAINTS_FILENAME,
                 *, profileCond = lambda x: True, accusedCond = lambda x: True, complaintCond = lambda x: True, prefix = CPDP_DATA_PREFIX) -> None:
        
        self.profileFilename = prefix + profileFilename
        self.accusedFilename = prefix + accusedFilename
        self.complaintsFilename = prefix + complaintsFilename
        
        self.profileCond = profileCond
        self.accusedCond = accusedCond
        self.complaintCond = complaintCond

    # returns a dict of profiles, keyed by UID
    def getProfileDict(self) -> dict[str, dict[str, str]]:
        profileDict: dict[str, dict[str, str]] = dict()
        with open(self.profileFilename, newline="") as profileFile:
    
        # cols: UID
        #       first_name	    last_name	    middle_initial	middle_initial2
        #       suffix_name	    birth_year	    race	        gender
        #       appointed_date	resignation_date	            current_status
        #       current_star	current_unit	current_rank	start_date
        #       org_hire_date	profile_count	cleaned_rank	link_UID

            profileCsv = csv.DictReader(profileFile)
            row: dict[str, str]
            for row in profileCsv:
                row["UID"] = row["UID"].removesuffix(".0")
                if not row["appointed_date"]:
                    row["appointed_date"] = DATE_MIN
                if not row["resignation_date"]:
                    row["resignation_date"] = DATE_MAX
                    
                # optionally filter rows
                if not self.profileCond(row): continue
                
                profileDict[row["UID"]] = row
        return profileDict
    
    # returns a list of complaints
    # each complaint is a dict consisting of an [accusation] and a [complaint] part
    def getComplaintList(self, profileDict: dict) -> list[dict[str]]:
        
        accusationDict: dict[str, list[dict[str, str]]] = dict()
        with open(self.accusedFilename, newline="") as accusationFile:
        
        # [accusation]
        # cols: cr_id
        #       UID	            complaint_category	            complaint_code
        #       cv	            final_finding	final_outcome	recc_finding	
        #       recc_outcome	link_UID
         
            accusationCsv = csv.DictReader(accusationFile)
            row: dict[str, str]
            for row in accusationCsv:
                row["UID"] = row["UID"].removesuffix(".0")
                
                # accusations must correspond to officers
                if row["UID"] not in profileDict: continue
                
                # optionally filter rows
                if not self.accusedCond(row): continue

                if row["cr_id"] not in accusationDict:
                    accusationDict[row["cr_id"]] = list()
                accusationDict[row["cr_id"]].append(row)


        complaintList: list[dict[str, str]] = list()
        with open(self.complaintsFilename, newline="") as complaintFile:
        
        # [complaint]
        # cols: cr_id
        #       cv	            incident_date	complaint_date	closed_date
        #      	add1	        add2	        beat	        city
        #      	full_address	location
            
            complaintCsv = csv.DictReader(complaintFile)
            row: dict[str, str]
            for row in complaintCsv:
                incidentDate: str = row["incident_date"]
                
                # filter all incidents not between 1990 and 2020
                # this is possible because YYYY-MM-DD format obeys lexicographic order
                if not (DATE_INITIAL <= incidentDate < DATE_FINAL):
                    continue
                
                # filter all incidents not corresponding to an accusation
                if (row["cr_id"] not in accusationDict):
                    continue
                
                # optionally filter rows
                if not self.complaintCond(row): continue
                
                complaintList.append(row)
            
            # sort by incident date
            complaintList.sort(key=lambda row: row["incident_date"])
                
        output: list[dict[str, dict[str, str]]] = list()
        
        row: dict[str, str]
        for row in complaintList:
            outputEntry: dict[str, dict[str, str]]
            outputEntry = {
                "complaint": row,
                "accusation": accusationDict[row["cr_id"]]
            }
            output.append(outputEntry)
        
        return output
    
    # returns a dict; keys are officer UIDs, values are the dates of all complaints in order
    # prerequisite: complaintList is sorted
    def allComplaintDates(self, complaintList: list[dict[str]]) -> dict[str, str]:
        output: dict[str, str] = dict()
        
        currentDate = DATE_MIN
        
        row: dict[str]
        for row in complaintList:
            assert row["complaint"]["incident_date"] >= currentDate
            currentDate = row["complaint"]["incident_date"]

            accusee: dict[str, str]
            for accusee in row["accusation"]:
                output.setdefault(accusee["UID"], list())
                output[accusee["UID"]].append(currentDate)
        
        return output
            