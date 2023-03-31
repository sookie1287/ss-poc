import os
import sys

currPath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(currPath)

from drivers.IamRoles import IamRoles

class Iam():
    def __init__(self):
        self.ok = 1
        
    def advise(self):
        r = IamRoles()
        r.run()
        r.showInfo()
    
        
if __name__ == "__main__":
    o = Iam()
    o.advise()
    