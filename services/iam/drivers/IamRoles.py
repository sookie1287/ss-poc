import sys
import os

currPath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(currPath + '/../../')

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
    