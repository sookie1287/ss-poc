import boto3
import botocore

import json
import time

from utils.Config import Config
from utils.Tools import _pr
from services.Service import Service
class S3(Service):
    def __init__(self, region):
        super().__init__(region)
        self.region = region
        
        self.s3Client = boto3.client('s3')
        self.s3Control = boto3.client('s3control')
        
        # buckets = Config.get('s3::buckets', [])
    
    def getResources():
        buckets = Config.get('s3::buckets', [])
        # $buckets = ['ap-southeast-1' => ['kuettai-personal']];
        if not buckets:
            buckets = []
            results = self.s3Client.list_buckets()
            
            arr = results.get('Buckets')
            while results.get('Maker') is not None:
                results = self.s3Client.list_buckets(
                    Maker = results.get('Maker')
                )    
                arr = arr + results.get('Buckets')
            
            for ind, bucket in enumerate(arr):
                loc = self.s3Client.get_bucket_location(
                    Bucket = bucket['Name'] 
                )
                
                reg = loc.get('LocationConstraint')
                buckets[reg].append(arr[ind])
            
            Config.set('s3::buckets', buckets)
        
        if self.region in buckets:
            _buckets = buckets[self.region]
        else:
            return []
            
        if not self.tags:
            return _buckets
        
        filteredBuckets = []
        for bucket in _buckets:
            try:
                result = self.s3Client.get_bucket_tagging(Bucket = bucket['Name'])
                tags =result.get('TagSet')
            
                if self.resourceHasTags(tags):
                    filteredBuckets.append(bucket)
            except S3E as e:
                ## Do nothing, no tags has been define;clear
                pass
            
        return filteredBuckets    
        
if __name__ == "__main__":
    o = S3('ap-southeast-1')
    o.advise()