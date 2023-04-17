import os
import boto3
from botocore.config import Config
from service.Service import Service

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/efs.html
class Efs(Service):
    def __init__(self, region):
        super().__init__(region)

        self.region = region
        self.__AWS_OPTIONS = self._Service__AWS_OPTIONS
        self.__AWS_OPTIONS['region_name'] = region

        config = Config(**self.__AWS_OPTIONS)
        self.efs_client = boto3.client('efs', config=config)

        self.__load_drivers()

    def get_resources(self):
        resources = self.efs_client.describe_file_systems()
        results = resources['FileSystems']

        if not self.tags:
            return results

        filtered_results = []
        for efs in results:
            if self.resource_has_tags(efs['Tags']):
                filtered_results.append(efs)

        return filtered_results

    def advise(self):
        objs = {}

        efs_list = self.get_resources()

        driver = 'efs_efs'
        if globals().get(driver):
            for efs in efs_list:
                print('... (EFS) inspecting ' + efs['FileSystemId'])
                obj = globals()[driver](efs, self.efs_client)
                obj.run()

                objs['EFS::' + efs['FileSystemId']] = obj.get_info()
                del obj

        return objs

    def __load_drivers(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drivers')
        files = os.listdir(path)
        for file in files:
            if file[0] == '.':
                continue

            with open(os.path.join(path, file), 'r') as f:
                exec(f.read(), globals())
