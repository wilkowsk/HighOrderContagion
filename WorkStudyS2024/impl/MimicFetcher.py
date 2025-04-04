import csv
import random
from collections import defaultdict

from impl.GlobalConsts import *

# acts the same as OffenseFetcher, but randomly assigns which officers are responsible for what offenses
class MimicFetcher:
    
    def __init__(self, profileFilename: str = PROFILE_FILENAME, accusedFilename: str = ACCUSED_FILENAME, complaintsFilename: str = COMPLAINTS_FILENAME,
                 *, profileCond = lambda x: True, accusedCond = lambda x: True, complaintCond = lambda x: True) -> None:
        prefix = CPDP_DATA_PREFIX
        
        self.profileFilename = prefix + profileFilename
        self.accusedFilename = prefix + accusedFilename
        self.complaintsFilename = prefix + complaintsFilename
        
        self.profileCond = profileCond
        self.accusedCond = accusedCond
        self.complaintCond = complaintCond

    # returns a dict of profiles, keyed by UID
    def getProfileDict(self) -> dict:
        profileDict = dict()
        with open(self.profileFilename, newline="") as profileFile:
    
        # cols: UID
        #       first_name	    last_name	    middle_initial	middle_initial2
        #       suffix_name	    birth_year	    race	        gender
        #       appointed_date	resignation_date	            current_status
        #       current_star	current_unit	current_rank	start_date
        #       org_hire_date	profile_count	cleaned_rank	link_UID

            profileCsv = csv.DictReader(profileFile)
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
    def getComplaintList(self, profileDict: dict):
        
        allOfficers = list(profileDict.keys())
        
        accusationDict = defaultdict(list)
        dupeCheckDict = defaultdict(list)    # used only to check duplicates
        with open(self.accusedFilename, newline="") as accusationFile:
        
        # [accusation]
        # cols: cr_id
        #       UID	            complaint_category	            complaint_code
        #       cv	            final_finding	final_outcome	recc_finding	
        #       recc_outcome	link_UID
         
            accusationCsv = csv.DictReader(accusationFile)
            for row in accusationCsv:
                row["UID"] = row["UID"].removesuffix(".0")
                
                # accusations must correspond to officers
                if row["UID"] not in profileDict: continue
                
                # optionally filter rows
                if not self.accusedCond(row): continue
                    
                # randomly select an officer not already selected before
                isValid = False
                while not isValid:
                    row["UID"] = random.choice(allOfficers)
                    if row["UID"] not in dupeCheckDict[row["cr_id"]]:
                        isValid = True
                
                accusationDict[row["cr_id"]].append(row)
                dupeCheckDict[row["cr_id"]].append(row["UID"])


        complaintList = list()
        with open(self.complaintsFilename, newline="") as complaintFile:
        
        # [complaint]
        # cols: cr_id
        #       cv	            incident_date	complaint_date	closed_date
        #      	add1	        add2	        beat	        city
        #      	full_address	location
            
            complaintCsv = csv.DictReader(complaintFile)
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
                
        output = list()
        
        for row in complaintList:
            outputEntry = {
                "complaint": row,
                "accusation": accusationDict[row["cr_id"]]
            }
            output.append(outputEntry)
        
        return output
    
    # returns a dict; keys are officer UIDs, values are the dates of all complaints in order
    # prerequisite: complaintList is sorted
    def allComplaintDates(self, complaintList) -> dict:
        output = dict()
        
        currentDate = DATE_MIN
        
        for row in complaintList:
            assert row["complaint"]["incident_date"] >= currentDate
            currentDate = row["complaint"]["incident_date"]

            for accusee in row["accusation"]:
                output.setdefault(accusee["UID"], list())
                output[accusee["UID"]].append(currentDate)
        
        return output
            