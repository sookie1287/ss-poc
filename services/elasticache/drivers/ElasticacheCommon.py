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
