import boto3
import botocore
from packaging.version import Version

from utils.Config import Config
from utils.Tools import _pr
from services.Service import Service
from services.elasticache.drivers.ElasticacheMemcached import ElasticacheMemcached
from services.elasticache.drivers.ElasticacheRedis import ElasticacheRedis


class Elasticache(Service):
    def __init__(self, region) -> None:
        super().__init__(region)
        self.elasticacheClient = boto3.client(
            'elasticache')
        self.latest_3versions = self.getTopEngineVersions(3)

    def getECClusterInfo(self):
        # list all Elasticahe clusters
        arr = []
        try:
            while True:
                if len(arr) == 0:
                    # init
                    resp = self.elasticacheClient.describe_cache_clusters(
                        ShowCacheNodeInfo=True)
                else:
                    # subsequent
                    resp = self.elasticacheClient.describe_cache_clusters(
                        ShowCacheNodeInfo=True, Marker=resp.get('Marker'))

                arr = resp.get('CacheClusters')

                if resp.get('Marker') is None:
                    break
        except botocore.exceptions.ClientError as e:
            # print out error to console for now
            print(e)

        return arr

    def getTopEngineVersions(self, n: int) -> dict[list]:
        lookup = {}

        def get_version(engine):
            ret = self.elasticacheClient.describe_cache_engine_versions(
                Engine=engine)
            engine_versions = [engine_version.get(
                'EngineVersion') for engine_version in ret.get('CacheEngineVersions')]
            return sorted([Version(v) for v in engine_versions], reverse=True)[:n]

        try:
            for i in ['memcached', 'redis']:
                lookup[i] = get_version(i)
        except botocore.exceptions.ClientError as e:
            # print out error to console for now
            print(e)

        return lookup

    def getAllInstanceOfferings(self) -> dict[list]:
        offering = {}

        while True:
            if len(offering) == 0:
                # init
                resp = self.elasticacheClient.describe_reserved_cache_nodes_offerings()
            else:
                # subsequent
                resp = self.elasticacheClient.describe_reserved_cache_nodes_offerings(
                    Marker=resp.get('Marker'))

            for i in resp.get('ReservedCacheNodesOfferings'):
                if i.get('ProductDescription') not in offering.keys():
                    offering[i.get('ProductDescription')] = set(
                        [i.get('CacheNodeType')])
                else:
                    offering[i.get('ProductDescription')].add(
                        i.get('CacheNodeType'))

            if resp.get('Marker') is None:
                break

        return offering

    def getLatestInstanceTypes(self):
        pass

    def advise(self):
        objs = {}
        self.cluster_info = self.getECClusterInfo()
        _pr(self.cluster_info)

        # loop through EC nodes
        if len(self.cluster_info) > 0:
            print("evaluating Elasticache Clusters")

        for cluster in self.cluster_info:
            if cluster.get('Engine') == 'memcached':
                obj = ElasticacheMemcached(cluster, self.elasticacheClient)
            if cluster.get('Engine') == 'redis':
                obj = ElasticacheRedis(cluster, self.elasticacheClient)

            if obj is not None:
                obj.run()
                objs[f'MemcachedCluster:{cluster.get("CacheClusterId")}'] = obj.getInfo(
                )
                del obj
            else:
                print(
                    f"Engine {cluster.get('Engine')} of Memcached Cluster {cluster.get('CacheClusterId')} is not recognised")

        return objs
    pass


# unit testing/invoke for class
if __name__ == "__main__":
    Config.init()
    o = Elasticache('us-east-1')
    # _pr(o.getAllInstanceOfferings())
    out = o.advise()
    _pr(out)
