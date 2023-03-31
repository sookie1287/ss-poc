import sys
sys.path.append('./../../')

from evaluator import Evaluator

class Roles(Evaluator):
    def tt(self):
        self.setV()
        print(self.v)
        
if __name__ == "__main__":
    r = Roles()
    r.tt()