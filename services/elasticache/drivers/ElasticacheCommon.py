from services.Evaluator import Evaluator


class ElasticacheCommon(Evaluator):
    def __init__(self, cluster, client):
        super().__init__()
        self.cluster = cluster
        self.client = client
    