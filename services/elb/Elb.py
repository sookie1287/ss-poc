import boto3
import botocore

import json
import time

from utils.Config import Config
from services.Service import Service

class Elb(Service):
    def __init__(self, region):
        super().__init__(region)
        self.ec2Client = boto3.client('ec2')
        self.elbClient = boto3.client('elb')
        self.elbClassicClient = boto3.client('elbClassic')
        self.asgClient = boto3.client('asg')

    def getELB(self):
        results = self.elbClient.describe_load_balancers()
        ## TODO, use describeTags
        
        arr = results.get('LoadBalancers')
        while results.get('NextToken') is not None:
            results = self.elbClient.describe_load_balancers(
                NextToken = results.get('NextToken')
            )
            
            arr = arr + results.get('LoadBalancers')
        
        if not self.tags:
            return arr
        
        filteredResults = []
        for ind, elb in enumerate(arr):
            ##Can supports up to 20 resources;
            tmp = self.elbClient.describe_tags(
                ResourceArns = [elb['LoadBalancerArn']]
            )
            
            tagDesc = tmp.get('TagDescriptions')
            if tagDesc and tagDesc[0] and tagDesc[0]['Tags'] and self.resource_has_tags(tagDesc[0]['Tags']):
                filteredResults.append(elb)
        
        return filteredResults
    
    def getELBClassic(self):
        results = self.elbClassicClient.describe_load_balancers()
        
        arr = results.get('LoadBalancerDescriptions')
        while results.get('NextToken') is not None:
            results = self.elbClient.describe_load_balancers(
                NextToken = results.get('NextToken')
            )
            
            arr = arr + results.get('LoadBalancers')
            
        return arr
    
    def getELBSecurityGroup(self, elb):
        if 'SecurityGroups' not in elb:
            return []
        
        securityGroups = elb['SecurityGroups']
        groupIds = []
        
        for groupId in securityGroups:
            groupIds.append(groupId)
        
        if not groupIds:
            return []
        
        param = {'GroupIds': groupIds}
        if self.tags:
            param['Filters'] = self.tags
        
        results = self.ec2Client.describeSecurityGroups(param)
        arr = results.get('SecurityGroups')
        while results.get('NextToken') is not None:
            param = {'NextToken': results.get('NextToken')}
            if self.tags:
                param['Filters'] = self.tags
            
            results = self.ec2Client.describeSecurityGroups(param)    
            arr = arr + results.get('SecurityGroups')
        
        return arr
    
    def getAsg(self):
        results = self.asgClient.describeAutoScalingGroups(Filters=self.tags)
        arr = results.get('AutoScalingGroups')
        
        while results.get('NextToken') is not None:
            results = self.asgClient.describeAutoScalingGroups(
                Filters=self.tags,
                NextToken=results.get('NextToken')
            )
            arr = results.get('AutoScalingGroups')
            
        return arr
    