# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html

import boto3
import botocore

import json
import time

from utils.Config import Config
from utils.Tools import Tools
from services.Service import Service

from services.Evaluator import Evaluator

class Ec2Common(Evaluator):
    def __init__(self, ec2Client):
        super().__init__()
        self.ec2Client = ec2Client
        
        self.init()
        
    def _checkInstanceTypeGeneration(self):
        instance = self.ec2['Instances'][0]
        
        # TO DO
        # instanceArr = __aws_parseInstanceFamily(instance['InstanceType'])
        instanceArr = {}
        instancePrefixArr = instanceArr['prefixDetail']
        instancePrefixArr['version'] += 1
        size = instanceArr['suffix']
        newFamily = instancePrefixArr['family'] + str(instancePrefixArr['version']) + instancePrefixArr['attributes']

        try:
            results = self.ec2Client.describe_instance_types(
                InstanceTypes=[newFamily + '.' + size]
            )
        except Exception as e:
            self.results['EC2NewGen'] = [1, instance['InstanceType']]
            return

        self.results['EC2NewGen'] = [-1, instance['InstanceType']]
        return
    
    def __checkDetailedMonitoringEnable(self):
        instance = self.ec2['Instances'][0]
        
        if instance['Monitoring']['State'] == 'disabled':
            self.results['EC2DetailedMonitor'] = [-1, instance['Monitoring']['State']]
        else:
            self.results['EC2DetailedMonitor'] = [1, instance['Monitoring']['State']]
        
        return
    
    def __checkIamProfileAssociate(self):
        instance = self.ec2['Instances'][0]
        instanceId = instance['InstanceId']
        results = self.ec2Client.describe_iam_instance_profile_associations(
            Filters=[
                {
                    'Name': 'instance-id',
                    'Values': [instanceId]
                }
            ]
        )
        if self.verifyIamProfileAssociate(results):
            self.results['EC2IamProfile'] = [1, results['IamInstanceProfileAssociations']['IamInstanceProfile']['Arn']]
        else:
            self.results['EC2IamProfile'] = [-1, '']
        return
    
    def verifyIamProfileAssociate(self,iamProfile):
        if not iamProfile['IamInstanceProfileAssociations']:
            return False
        else:
            return True
            
    def __checkEIPInUsed(self):
        eipList = self.ec2Client.describeAddresses()
    
        for eip in eipList['Addresses']:
            if 'AssociationId' not in eip:
                self.results['EC2EIPInUsed'] = [-1, eip['PublicIp']]
                return

    def __checkCWMemoryMetrics(self):
        # cwClient = CW.getClient()
        # instance = self.ec2['Instances'][0]
    
        # dimensions = [
        #     {
        #         'Name': 'InstanceId',
        #         'Value': instance['InstanceId']
        #     }
        # ]
    
        # result = cwClient.listMetrics([
        #     'MetricName': 'mem_used_percent',
        #     'Namespace': 'CWAgent',
        #     'Dimensions': dimensions
        # ])
    
        # if result['Metrics']:
        #     return
    
        # result = cwClient.listMetrics([
        #     'MetricName': 'Memory % Committed Bytes In Use',
        #     'Namespace': 'CWAgent',
        #     'Dimensions': dimensions
        # ])
    
        # if result['Metrics']:
        #     return
    
        # self.results['EC2MemoryMonitor'] = [-1, 'Disabled']
        return
    
    def __checkCWDiskMetrics(self):
        global CW
        cwClient = CW.getClient()
        instance = ec2['Instances'][0]
    
        dimensions = [
            {
                'Name': 'InstanceId',
                'Value': instance['InstanceId']
            }
        ]
    
        result = cwClient.listMetrics([
            'MetricName': 'disk_used_percent',
            'Namespace': 'CWAgent',
            'Dimensions': dimensions
        ])
    
        if not result['Metrics']:
            return
    
        result = cwClient.listMetrics([
            'MetricName': 'LogicalDisk % Free Space',
            'Namespace': 'CWAgent',
            'Dimensions': dimensions
        ])
    
        if not result['Metrics']:
            results['EC2DiskMonitor'] = [-1, 'Disabled']
            return

    def __checkEC2Active(self):
        global CW
    
        verifyDay = 7
    
        cwClient = CW.getClient()
        instance = ec2['Instances'][0]
    
        launchTime = instance['LaunchTime']
        launchDay = (strtotime('now') - strtotime(launchTime))/(60 * 60 * 24)
        if launchDay < verifyDay:
            return
    
        dimensions = [
            {
                'Name': 'InstanceId',
                'Value': instance['InstanceId']
            }
        ]
    
        results = cwClient.getMetricStatistics([
            'Dimensions': dimensions,
            'Namespace': 'AWS/EC2',
            'MetricName': 'CPUUtilization',
            'StartTime': strtotime('-7 days'),
            'EndTime': strtotime('now'),
            'Period': verifyDay * 24 * 60 * 60,
            'Statistics': ['Average'],
            # 'Unit': 'None'
        ])
    
        if not results['Datapoints']:
            results['EC2Active'] = [-1, 'Inactive']
    
        return
    
    def __checkSecurityGroupNo(self):
        instance = self.ec2['Instances'][0]
        
        if len(instance['SecurityGroups']) > 50:
            self.results['EC2SGNumber'] = [-1, len(instance['SecurityGroups'])]
        return
    
    def getEC2UtilizationMetrics(self, metricName, verifyDay):
        cwClient = CW.getClient()
        instance = self.ec2['Instances'][0]
        
        dimensions = [
            {
                'Name': 'InstanceId',
                'Value': instance['InstanceId']
            }
        ]
        
        results = cwClient.getMetricStatistics(
            Dimensions = dimensions,
            Namespace = 'AWS/EC2',
            MetricName = metricName,
            StartTime = time.strftime('-%s days' % verifyDay),
            EndTime = time.strftime('now'),
            Period = 24 * 60 * 60,
            Statistics = ['Average'],
            # Unit = 'None'
        )
        
        return results
        
    def checkMetricsLowUsage(self, mericName, verifyDay, thresholdDay, thresholdValue):
        result = getEC2UtilizationMetrics(mericName, verifyDay)
        
        cnt = 0
        if len(result['Datapoints']) < verifyDay:
            ## Handling if EC2 is stopped
            cnt = verifyDay - len(result['Datapoints'])
            
        for datapoint in result['Datapoints']:
            if datapoint['Average'] < thresholdValue:
                cnt += 1
                
        if cnt < thresholdDay:
            return False
        else:
            return True
        
    def __checkEC2LowUtilization(self):
        instance = ec2['Instances'][0]
        
        verifyDay = 14
        thresholdDay = 4
        
        launchTime = instance['LaunchTime']
        launchDay = (datetime.now() - datetime.strptime(launchTime)).days
        if launchDay < verifyDay:
            return
        
        cpuThresholdPercent = 10
        cpuLowUsage = checkMetricsLowUsage('CPUUtilization', verifyDay, thresholdDay, cpuThresholdPercent)
        if not cpuLowUsage:
            return
        
        networkThresholdByte = 5 * 1024 * 1024
        networkOutLowUsage = checkMetricsLowUsage('NetworkOut', verifyDay, thresholdDay, networkThresholdByte)
        if not networkOutLowUsage:
            return
        
        networkInLowUsage = checkMetricsLowUsage('NetworkIn', verifyDay, thresholdDay, networkThresholdByte)
        if not networkInLowUsage:
            return
        
        results['EC2LowUtilization'] = [-1, '']
        return
    
    def checkMetricsHighUsage(self, mericName, verifyDay, thresholdDay, thresholdValue):
        result = getEC2UtilizationMetrics(mericName, verifyDay)
        
        if len(result['Datapoints']) < verifyDay:
            return False
        
        cnt = 0
        for datapoint in result['Datapoints']:
            if datapoint['Average'] > thresholdValue:
                cnt += 1
        
        if cnt < thresholdDay:
            return False
        else:
            return True
    
    def __checkEC2HighUtilization(self):
        instance = ec2['Instances'][0]
        
        verifyDay = 14
        thresholdDay = 4
        
        launchTime = instance['LaunchTime']
        launchDay = (datetime.now() - datetime.strptime(launchTime))/(60 * 60 * 24)
        if launchDay < verifyDay:
            return
        
        cpuThresholdPercent = 90
        cpuHighUsage = checkMetricsHighUsage('CPUUtilization', verifyDay, thresholdDay, cpuThresholdPercent)
        if not cpuHighUsage:
            return
        
        results['EC2HighUtilization'] = [-1, '']
        return