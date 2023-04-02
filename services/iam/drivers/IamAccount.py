import boto3
import botocore

import datetime
from dateutil.tz import tzlocal

from .IamCommon import IamCommon
 
class IamAccount(IamCommon):
    PASSWORD_POLICY_MIN_SCORE = 4
    
    def __init__(self, none, iamClient):
        super().__init__()
        self.iamClient = iamClient
        # self.__configPrefix = 'iam::settings::'
        
        self.init()
        
    def passwordPolicyScoring(self, policies):
        score = 0
        for policy, value in policies.items():
            ## no score for this:
            if policy in ['AllowUsersToChangePassword', 'ExpirePasswords']:
                continue
            
            if policy == 'MinimumPasswordLength' and value >= 8:
                score += 1
                continue
            
            if policy == 'MaxPasswordAge' and value <= 90:
                score += 1
                continue
            
            if policy == 'PasswordReusePrevention' and value >= 3:
                score += 1
                continue
            
            if not value is None and value > 0:
                score += 1
                
        return score
        
    def _checkPasswordPolicy(self):
        try:
            resp = self.iamClient.get_account_password_policy()
            policies = resp.get('PasswordPolicy')
            
            score = self.passwordPolicyScoring(policies)
            
            currVal = []
            if score <= self.PASSWORD_POLICY_MIN_SCORE:
                for policy, num in policies.items():
                    currVal.append(f"{policy}={num}")
                    
                output = '<br>'.join(currVal)
                self.results['passwordPolicyWeak'] = [-1, output]
                
        except botocore.exceptions.ClientError as e:
            ecode = e.response['Error']['Code']
            print(ecode)
            if ecode == 'NoSuchEntity':
                self.results['passwordPolicy'] = [-1, ecode]