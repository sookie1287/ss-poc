from .drivers.IamRoles import IamRoles

class Iam():
    def __init__(self):
        self.ok = 1
        
    def advise(self):
        r = IamRoles()
        r.run()
    
        
if __name__ == "__main__":
    o = Iam()
    o.advise()
    