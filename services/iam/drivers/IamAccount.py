import boto3
import botocore

import datetime
from dateutil.tz import tzlocal

from utils.Config import Config
from .IamCommon import IamCommon
 
class IamAccount(IamCommon):
    PASSWORD_POLICY_MIN_SCORE = 4
    
    def __init__(self, none, iamClient, accClient, sppClient, noOfUsers):
        super().__init__()
        self.iamClient = iamClient
        self.accClient = accClient
        self.sppClient = sppClient
        self.noOfUsers = noOfUsers
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
    
    def _checkSupportPlan(self):
        sppClient = self.sppClient
        try:
            resp = sppClient.describeSeverityLevels()
        except botocore.exceptions.ClientError as e:
            ecode = e.response['Error']['Code']
            if ecode == 'SubscriptionRequiredException':
                self.results['supportPlanLowTier'] = [-1, '']
    
    def _checkHasUsers(self):
        # has at least 1 for all account (root)
        if self.noOfUsers < 2:
            self.results['noUsersFound'] = [-1, 'No IAM User found']
                
    def _checkHasAlternateContact(self):
        CONTACT_TYP = ['BILLING', 'SECURITY', 'OPERATIONS']
        cnt = 0
        for typ in CONTACT_TYP:
            res = self.getAlternateContactByType(typ)
            cnt += res
        
        if cnt == 0:
            self.results['hasAlternateContact'] = [-1, 'No alternate contacts']

    
    def getAlternateContactByType(self, typ):
        stsInfo = Config.get('stsInfo')
        try:
            resp = self.accClient.get_alternate_contact(
                AlternateContactType = typ
            )
            return 1
            
        except botocore.exceptions.ClientError as e:
            ecode = e.response['Error']['Code']
            if ecode == 'ResourceNotFoundException':
                return 0