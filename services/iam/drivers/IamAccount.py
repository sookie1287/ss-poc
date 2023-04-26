import boto3
import botocore

import datetime
from dateutil.tz import tzlocal

from utils.Config import Config
from .IamCommon import IamCommon
 
class IamAccount(IamCommon):
    PASSWORD_POLICY_MIN_SCORE = 4
    
    def __init__(self, none, awsClients, noOfUsers):
        super().__init__()
        
        self.iamClient = awsClients['iamClient']
        self.accClient = awsClients['accClient']
        self.sppClient = awsClients['sppClient']
        self.gdClient = awsClients['gdClient']
        self.budgetClient = awsClients['budgetClient']
        
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
    
    def _checkHasGuardDuty(self):
        ## randomly check 1 region
        # $results = $this->guarddutyClient->listDetectors();
        # $arr = $results->get('DetectorIds');
        resp = self.gdClient.list_detectors()
        print(resp)
        
    def _checkHasCostBudget(self):
        stsInfo = Config.get('stsInfo')
        
        budgetClient = self.budgetClient
        resp = budgetClient.describe_budgets(AccountId=stsInfo['Account'])
        
        if 'Budgets' in resp:
            return 
        
        self.results['enableCostBudget'] = [-1, ""]
        
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
            resp = sppClient.describe_severity_levels()
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
        try:
            resp = self.accClient.get_alternate_contact(
                AlternateContactType = typ
            )
            return 1
            
        except botocore.exceptions.ClientError as e:
            ecode = e.response['Error']['Code']
            if ecode == 'ResourceNotFoundException':
                return 0