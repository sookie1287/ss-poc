import boto3
import botocore

from utils.Config import Config
from utils.Tools import _pr
from services.Service import Service
##import drivers here
from services.rds.drivers.RdsCommon import RdsCommon

class Rds(Service):
    def __init__(self, region):
        super().__init__(region)
        self.rdsClient = boto3.client('rds')

    engineDriver = {
        'mysql': 'mysql',
        'aurora-mysql': 'mysql_aurora',
        'postgres': 'postgres',
        'aurora-postgresql': 'postgres_aurora'
    }
    
    def getResources(self):
        results = self.rdsClient.describe_db_instances()
        
        arr = results.get('DBInstances')
        while results.get('Maker') is not None:
            results = self.ec2Client.describe_db_instances(
                Maker = results.get('Maker')
            )
            arr = arr + results.get('DBInstances')
        
        if not self.tags:
            return arr
        
        finalArr = []
        for i, detail in enumerate(arr):
            if self.resourceHasTags(detail['TagList']):
                finalArr.append(arr[i])
        
        return finalArr    
    
    def advise(self):
        objs = []
        instances = self.getResources()
        
        for instance in instances:
            print('... (RDS) inspecting ' + instance['DBInstanceIdentifier'])
            
            engine = instance['Engine']
            if engine not in self.engineDriver:
                continue
            
            engine = self.engineDriver[engine]
                        
            driver = 'rds_' + engine
            print(globals())
            if driver in globals():
                obj = globals()[driver](instance, self.rdsClient)
                obj.run()
                
                objs[instance['Engine'] + '::' + instance['DBInstanceIdentifier']] = obj.getInfo()
                del obj
           
        return objs
    
if __name__ == "__main__":
    Config.init()
    o = Rds('ap-southeast-1')
    out = o.advise()
    _pr(out)