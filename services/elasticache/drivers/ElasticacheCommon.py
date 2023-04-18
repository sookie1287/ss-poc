from services.Evaluator import Evaluator


class ElasticacheCommon(Evaluator):
    def __init__(self, cluster, client):
        super().__init__()
        self.cluster = cluster
        self.client = client

    def _checkEncryption(self):
        stringBuild = []
        if self.cluster.get('TransitEncryptionEnabled') is not True:
            stringBuild.append('in transit')
        if self.cluster.get('AtRestEncryptionEnabled') is not True:
            stringBuild.append('at rest')
        
        if len(stringBuild) > 0:
            self.results['EncInTransitAndRest'] = [-1, f"Not using encryption {' and '.join(stringBuild)}"]
    
    def _checkDefaultParamGroup(self):
        if self.cluster.get('CacheParameterGroup').get('CacheParameterGroupName').startswith("default."):
            self.results['DefaultParamGroup'] = [-1, "Using default parameter group"]
    
    def _checkRInstanceFamily(self):
        instance_type = self.cluster.get('CacheNodeType').lstrip('cache.')
        if instance_type[0] != 'r':
            self.results['RinstanceType'] = [-1, f"using {instance_type}"]

