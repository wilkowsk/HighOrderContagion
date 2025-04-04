from impl.CountCollections import CountList

class RiskCounts:
    def __init__(self):
        self.internalList: CountList = CountList()
        
    def update(self, newList: CountList, reverse: bool = False):
        self.internalList.addAll(newList, reverse)
            
    def getState(self):
        output = CountList()
        output.addAll(self.internalList)
        return output