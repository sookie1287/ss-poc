import urllib.parse
from datetime import date

import boto3

from utils.Config import Config
from utils.Policy import Policy
from services.Evaluator import Evaluator

class S3Bucket(Evaluator):
    def __init__(self, bucket, s3Client):
        super().__init__()
        self.bucket = bucket
        self.s3Client = s3Client
        
        self.init()