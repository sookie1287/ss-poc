# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html

import boto3
import botocore

import json
import time

from utils.Config import Config
from services.Service import Service
from services.ec2.drivers.Ec2Instance import Ec2Instance
from services.ec2.drivers.Ec2CompOpt import Ec2CompOpt

class Ec2(Service):
    def __init__(self, region):
        super().__init__(region)
        self.ec2Client = boto3.client('ec2')
        self.ssmClient = boto3.client('ssm')
        self.compOptClient = boto3.client('compute-optimizer')
    
    # get EC2 Instance resources
    def getResources(self):
        filters = []
        if self.tags:
            filters = self.tags
                
        results = self.ec2Client.describe_instances(
            Filters = filters
        )
        
            
        arr = results.get('Reservations')
        while results.get('NextToken') is not None:
            results = self.ec2Client.describe_instances(
                Filters = filters,
                NextToken = results.get('NextToken')
            )    
            arr = arr + results.get('Reservations')

        return arr
    
    # get EC2 Security Group resources
    def getEC2SecurityGroups(self,instance):
        if 'SecurityGroups' in instance:
            securityGroups = instance['SecurityGroups']
            param = {}
            groupIds = []
            for group in securityGroups:
                groupIds.append(group['GroupId'])
            if not groupIds:
                return []
            param ['GroupIds'] = groupIds
            print(param)
            if self.tags:
                param['Filters'] = self.tags
                
            results = self.ec2Client.describe_security_groups(
                GroupIds = groupIds
            )
                
            arr = results.get('SecurityGroups')
            while results.get('NextToken') is not None:
                results = self.ec2Client.describeSecurityGroups(
                    GroupIds = groupIds,
                    NextToken = results.get('NextToken')
                    )
                arr = arr + results.get('SecurityGroups')
            return arr
    
    # in the original PHP edition, related services were together. now split it to EC2, ELB, ASG
    # EC2 Cost Explorer resources
    # EC2 Instance resources
    # EC2 EBS resources
    # EC2 Instance Security Group resources
    
    # EC2 ELB resources
    # EC2 ELB Classic resources
    # EC2 ELB Security Group resources
    
    # EC2 Autoscaling Group resources
            
    # def getEBS(self):
    #     param = {}
    #     # if self.tags:
    #     #     param['Filters'] = self.tags
        
    #     # results = self.ec2Client.describe_volumes(param)
    #     results = self.ec2Client.describe_volumes()
    #     arr = results.get('Volumes')
        
    #     while results.get('NextToken') is not None:
    #         # param = {'NextToken': results.get('NextToken')}
    #         # if self.tags:
    #         #     param['Filters'] = self.tags
                
    #         # results = self.ec2Client.describe_volumes(param)
    #         results = self.ec2Client.describe_volumes(
    #             NextToken = results.get('NextToken')
    #         )
    #         arr = arr + results.get('Reservations')
        
    #     return arr
        
    def advise(self):
        objs = {}
        instances = self.getResources()
        
        # self._AWS_OPTIONS['region']
        try:
            compOptPath = "/aws/service/global-infrastructure/regions/" + self._AWS_OPTIONS['region'] + "/services/compute-optimizer";
            compOptCheck = self.ssmClient.get_parameters_by_path(
                Path = compOptPath    
            )
            
            if 'Parameters' in compOptCheck and len(compOptCheck['Parameters']) > 0:
                print('... (Compute Optimizer) inspecting')
                obj = Ec2CompOpt(self.compOptClient)
                obj.run()
                
        except Exception as e:
            print(e)
            print("!!! Skipping compute optimizer check for <" + self._AWS_OPTIONS['region'] + ">")
        
        # print(results)
        
        for instance in instances:
            instanceData = instance['Instances'][0]
            # print(instanceData)
            print('... (EC2) inspecting ' + instanceData['InstanceId'])
            obj = Ec2Instance(instanceData,self.ec2Client)
            obj.run()
        
        return objs
        
        
    
if __name__ == "__main__":
    Config.init()
    o = Ec2('ap-southeast-1')
    output = o.advise()
    print(output)
    # results = o.getResources()
    # for result in results:
    #     if 'Instances' in result.keys():
    #         for instance in result['Instances']:
    #             print('... (EC2::Instance) inspecting ' + instance['InstanceId'])
    #             print("\n")
                
    #             sgResults = o.getEC2SecurityGroups(instance)
    #             print(sgResults)
                
    # results = o.getEBS()
    # print(results)
                
    
        # if 'Instances' in instance.key() and 0 in  instance['Instances'].key() and 'In'
        # print('... (EC2::Instance) inspecting ' + instance['Instances'])
        
        # print(instance)
        # print("\n")
    # print(out)