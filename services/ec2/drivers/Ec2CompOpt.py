import boto3
import botocore

from utils.Config import Config
from utils.Tools import Tools
from services.Service import Service

from services.Evaluator import Evaluator

class Ec2CompOpt(Evaluator):
    def __init__(self, compOptClient):
        super().__init__()
        self.compOptClient = compOptClient
        self.init()
    