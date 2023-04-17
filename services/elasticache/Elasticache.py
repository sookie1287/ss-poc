import boto3
import botocore

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

    def getECClusterInfo(self):
        # list all Elasticahe clusters
        arr = []
        try:
            resp = self.elasticacheClient.describe_cache_clusters(
                ShowCacheNodeInfo=True)
            arr = resp.get('CacheClusters')
            while resp.get('Marker') is not None:
                resp = self.elasticacheClient.describe_cache_clusters(
                    ShowCacheNodeInfo=True, Marker=resp.get('Marker'))
                arr = arr.append(resp.get('CacheClusters'))
            return arr

        except botocore.exceptions.ClientError as e:
            # print out error to console for now
            print(e)
            return arr

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
                objs['placeholder'] = obj.getInfo()
                del obj
            else:
                print(f"Engine {cluster.get('Engine')} not recognised")

        return objs
    pass


# unit testing/invoke for class
if __name__ == "__main__":
    Config.init()
    o = Elasticache('us-east-1')
    out = o.advise()
    _pr(out)
