from typing import Any


class CountDict(object):
    def __init__(self) -> None:
        self.internalDict: dict[Any, dict[Any, int | float]] = dict()

    # adds the given count at key and value
    def add(self, key, value, count: int | float = 1) -> None:
        self.internalDict[key][value] = self.read(key, value) + count
    
    # returns the count at the given key and value
    def read(self, key, value) -> int | float:
        if key not in self.internalDict:
            self.internalDict[key] = dict()    
        if value not in self.internalDict[key]:
            self.internalDict[key][value] = 0
        return self.internalDict[key][value]

    def maxKey(self) -> int | float:
        return max(self.internalDict.keys())
    
    def allKeys(self):
        return self.internalDict.keys()
    
class CountList(object):
    def __init__(self):
        self.internalDict: dict = dict()
    
    # adds the given count at key
    def add(self, key, count: int | float = 1) -> None:
        self.internalDict[key] = self.read(key) + count
        
        # key with value of 0 is equivalent to missing key
        if self.internalDict[key] == 0:
            self.internalDict.pop(key)
            
    def addAll(self, newList: "CountList", reverse: bool = False) -> None:
        multiplier: int = -1 if reverse else 1
        for key in newList.allKeys():
            self.add(key, newList.read(key) * multiplier)
        
    # returns the count at the given key
    def read(self, key) -> int | float:
        if key not in self.internalDict:
            # missing key is equivalent to key with value of 0
            return 0
        return self.internalDict[key]
    
    def maxKey(self) -> int | float:
        return max(self.internalDict.keys())

    def allKeys(self):
        return self.internalDict.keys()
    
    def __str__(self) -> str:
        return str(self.internalDict)
    
    def __eq__(self, __value: object) -> bool:
        if self is __value:
            return True
        elif type(self) != type(__value):
            return False
        else:
            return self.internalDict == __value.internalDict
        
    def __hash__(self) -> int:
        output = 0
        for key in self.allKeys():
            output += hash(key) * self.internalDict[key]
        return output
    
    def __str__(self) -> str:
        return str(self.internalDict)