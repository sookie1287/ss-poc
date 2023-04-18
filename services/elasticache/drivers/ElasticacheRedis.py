from .ElasticacheCommon import ElasticacheCommon
from packaging.version import Version


class ElasticacheRedis(ElasticacheCommon):
    def __init__(self, cluster, client):
        super().__init__(cluster, client)
        # self.init()

    def _checkDefaultPort(self):
        # TODO: check if multiple ports can be active in a given cluster
        ports_in_cluster = [node.get('Endpoint').get(
            'Port') for node in self.cluster.get('CacheNodes')]
        if any(port == 6379 for port in ports_in_cluster):
            self.results['DefaultPort'] = [-1,
                                           f"Using default Redis port 6379"]

    def _checkEngineVersion(self):
        if Version(self.cluster.get('EngineVersion')) not in self.latest_3versions.get('redis'):
            self.results['EngineVersion'] = [-1,
                                             f"Not using 3 latest versions"]
