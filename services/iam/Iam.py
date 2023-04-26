import boto3
import botocore

import json
import time

from utils.Config import Config
from utils.Tools import _pr
from services.Service import Service
from services.iam.drivers.IamRole import IamRole
from services.iam.drivers.IamGroup import IamGroup
from services.iam.drivers.IamUser import IamUser
from services.iam.drivers.IamAccount import IamAccount

class Iam(Service):
    def __init__(self, region):
        super().__init__(region)
        # self._AWS_OPTIONS['version'] = Config.AWS_SDK['IAMCLIENT_VERS']
        # self.iamClient = IamClient(self.__AWS_OPTIONS)
        self.iamClient = boto3.client('iam')
        self.accClient = boto3.client('account')
        self.sppClient = boto3.client('support')
    
    def getGroups(self):
        arr = []
        results = self.iamClient.list_groups()
        arr = results.get('Groups')
        
        while results.get('Marker') is not None:
            results = self.iamClient.list_groups(
                Marker = results.get('Marker')
            )
            arr = arr + results.get('Groups')
            
        return arr
    
    def getRoles(self):
        arr = []
        results = self.iamClient.list_roles()
        for v in results.get('Roles'):
            if (v['Path'] != '/service-role/' and v['Path'][0:18] != '/aws-service-role/') and (self._roleFilterByName(v['RoleName'])):
                arr.append(v)
                
        while results.get('Marker') is not None:
            results = self.iamClient.list_roles(Marker=results.get('Marker'))
            for v in results.get('Roles'):
                if (v['Path'] != '/service-role/' and v['Path'][0:18] != '/aws-service-role/') and (self._roleFilterByName(v['RoleName'])):
                    arr.append(v)
        
        return arr
        
    def getUsers(self):
        arr = []
        resp = self.iamClient.generate_credential_report()
        time.sleep(1)
        try:
            results = self.iamClient.get_credential_report()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ReportNotPresent':
                resp = self.iamClient.generate_credential_report()
                print('Generating IAM Credential Report...')
                time.sleep(1)
                
                results = self.iamClient.get_credential_report()
        
        rows = results.get('Content')
        rows = rows.decode('UTF-8')
        
        row = rows.split("\n")
        
        fields = row[0].split(',')
        del row[0]
        for temp in row:
            arr.append(dict(zip(fields, temp.split(','))))
        
        return arr
        
    def advise(self):
        objs = {}
        users = self.getUsers()
        
        print('... (IAM:Account) inspecting')
        obj = IamAccount(None, self.iamClient, self.accClient, self.sppClient, len(users))
        obj.run()
        objs['Account::Config'] = obj.getInfo()
        
        for user in users:
            print('... (IAM::User) inspecting ' + user['user'])
            obj = IamUser(user, self.iamClient)
            obj.run()
            
            identifier = "<b>root_id</b>" if user['user'] == "<root_account>" else user['user']
            objs['User::' + identifier] = obj.getInfo()
            del obj
        '''
        roles = self.getRoles()
        for role in roles:
            print('... (IAM::Role) inspecting ' + role['RoleName'])
            obj = IamRole(role, self.iamClient)
            obj.run()
            
            objs['Role::' + role['RoleName']] = obj.getInfo()
            del obj
        
        groups = self.getGroups()
        for group in groups:
            print('... (IAM::Group) inspecting ' + group['GroupName'])
            obj = IamGroup(group, self.iamClient)
            obj.run()
            
            objs['Group::' + group['GroupName']] = obj.getInfo()
            del obj
        '''
        return objs
    
    def _roleFilterByName(self, rn):
        keywords = [
            'AmazonSSMRole',
            'DO-NOT-DELETE',
            'Isengard',
            'AWSReservedSSO_',
            'AwsSecurityNacundaAudit',
            'AwsSecurityAudit',
            'GatedGarden',
            'PVRE-SSMOnboarding',
            'PVRE-Maintenance',
            'InternalAuditInternal'
        ]
        
        for kw in keywords:
            if kw in rn:
                return False
        return True
        
if __name__ == "__main__":
    Config.init()
    o = Iam('us-east-1')
    out = o.advise()
    _pr(out)
    