import boto3
import botocore
import datetime

from utils.Config import Config
from services.Service import Service

from services.Evaluator import Evaluator

class CostExplorerRecs(Evaluator):
    
    def __init__(self,ceClient):
        super().__init__()
        self.ceClient = ceClient
        self.init()
   
   # checks
  
    def _checkRIRecommendations(self):
        results = {}
        try:
            results = self.ceClient.get_reservation_purchase_recommendation({
                'Service': 'Amazon Elastic Compute Cloud - Compute'
                })
        except Exception as e:
            print('Reserved Instance recommendation API call is getting the following error:')
            print(e)
        
        if len(results) > 0:
            self.results['CEReservedInstance'] = ['-1','']
        
        return
    
    def _checkSPRecommendations(self):
        results = {}
        try:
            results = self.ceClient.get_savings_plan_purchase_recommendation({
                'LookbackPeriodInDays': 'THIRTY_DAYS',
                'PaymentOption': 'NO_UPFRONT',
                'SavingsPlansType': 'COMPUTE_SP',
                'TermInYears': 'ONE_YEAR'
                })
            if len(results) < 1:
                return;
            
            if results['SavingsPlansPurchaseRecommendation'] in results and len(results['SavingsPlansPurchaseRecommendation']['SavingsPlansPurchaseRecommendationDetails'])>0:
                self.results['CESavingsPlans'] = ['-1','']
        except Exception as e:
            print('Compute Savings Plans recommendation API call is getting the following error:')
            print(e) 
        
        
        return 