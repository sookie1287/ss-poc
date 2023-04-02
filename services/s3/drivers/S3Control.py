import urllib.parse
from datetime import date

import boto3

from utils.Config import Config
from utils.Policy import Policy
from services.Evaluator import Evaluator

class S3Control(Evaluator):
    def __init__(self, s3Control):
        super().__init__()
        self.s3Control = s3Control
        
        self.init()