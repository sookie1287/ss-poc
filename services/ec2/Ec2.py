# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html

import boto3
import botocore

import json
import time

from utils.Config import Config
from services.Service import Service
from services.ec2.drivers.Ec2Instance import Ec2Instance
from services.ec2.drivers.Ec2CompOpt import Ec2CompOpt
from services.ec2.drivers.EbsVolume import EbsVolume

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
    
    def getEBSResources(self):
        filters = []
        
        if self.tags:
            filters = self.tags
        
        results = self.ec2Client.describe_volumes(
            Filters = filters
        )
        
        arr = results.get('Volumes')
        while results.get('NextToken') is not None:
            results = self.ec2Client.describe_volumes(
                Filters = filters,
                NextToken = results.get('NextToken')
            )    
            arr = arr + results.get('Reservations')

        return arr
    
    def advise(self):
        objs = {}
        instances = self.getResources()
        
        # compute optimizer checks
        try:
            compOptPath = "/aws/service/global-infrastructure/regions/" + self._AWS_OPTIONS['region'] + "/services/compute-optimizer";
            compOptCheck = self.ssmClient.get_parameters_by_path(
                Path = compOptPath    
            )
            
            if 'Parameters' in compOptCheck and len(compOptCheck['Parameters']) > 0:
                print('... (Compute Optimizer) inspecting')
                obj = Ec2CompOpt(self.compOptClient)
                obj.run()
                
                #set to final output
                objs['ComputeOptimizer'] = obj.getInfo()
                del obj
                
        except Exception as e:
            print(e)
            print("!!! Skipping compute optimizer check for <" + self._AWS_OPTIONS['region'] + ">")
        
        # EC2 instance checks
        for instance in instances:
            instanceData = instance['Instances'][0]
            print('... (EC2) inspecting ' + instanceData['InstanceId'])
            obj = Ec2Instance(instanceData,self.ec2Client)
            obj.run()
            
            #set to final output
            objs['EC2::' + instanceData['InstanceId']] = obj.getInfo()
            del obj
        
        #EC2 Security group checks
        #EC2 Cost Explorer checks
        
        #EBS checks
        volumes = self.getEBSResources()
        
        for volume in volumes:
            # print(volume)
            print('... (EBS) inspecting ' + volume['VolumeId'])
            obj = EbsVolume(volume,self.ec2Client)
            obj.run()
            
            #set to final output
            objs['EBS::' + volume['VolumeId']] = obj.getInfo()
            del obj
        
        return objs
        
        
    
if __name__ == "__main__":
    Config.init()
    o = Ec2('ap-southeast-1')
    output = o.advise()
    print(output)