from .ElasticacheCommon import ElasticacheCommon
from packaging.version import Version


class ElasticacheMemcached(ElasticacheCommon):
    def __init__(self, cluster, client):
        super().__init__(cluster, client)
        # self.init()

    def _checkDefaultPort(self):
        # Memcached returns ConfigurationEndpoint with port information
        # self.cluster.get('ConfigurationEndpoint').get('Port')
        # self.cluster.get('CacheNodes')[0].get('Endpoint').get('Port')
        if self.cluster.get('ConfigurationEndpoint').get('Port') == 11211:
            self.results['DefaultPort'] = [-1,
                                           f"Using default Memcached port 11211"]

    def _checkEngineVersion(self):
        if Version(self.cluster.get('EngineVersion')) not in self.latest_3versions.get('memcached'):
            self.results['EngineVersion'] = [-1,
                                             f"Not using 3 latest versions"]
