import sys
import os 
from pathlib import Path

# any cleaner way to import without cluttering sys.path?
path = (Path(__file__).resolve().parent.parent.parent)
if path not in sys.path:
    sys.path.append(str (path)+os.sep)

from Evaluator import Evaluator

class IamRoles(Evaluator):
    def tt(self):
        pass
        
    def _checkMocktest(self):
        self.results['Mocktest'] = [-1, 'GG']
    
    def _checkMocktest2(self):    
        self.results['Mocktest2'] = [-1, 'GG']
        
if __name__ == "__main__":
    r = IamRoles()
    r.tt()
    