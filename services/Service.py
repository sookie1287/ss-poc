from utils.Config import Config

class Service:
    _AWS_OPTIONS = {}
    RULESPREFIX = None
    tags = []

    TAGS_SEPARATOR = '%'
    KEYVALUE_SEPARATOR = '='
    VALUES_SEPARATOR = ','

    def __init__(self, region):
        global _Config
        # global PHPSDK_CRED_PROVIDER, PHPSDK_CRED_PROFILE

        classname = self.__class__.__name__

        suffix = "" if classname in Config.GLOBAL_SERVICES else " on region <" + region + ">"
        # __info("Scanning " + classname + suffix)

        self.RULESPREFIX = classname + '::rules'
        self._AWS_OPTIONS = Config.get("_AWS_OPTIONS", {'PlaceHolder': 'ok'})
        self._AWS_OPTIONS['region'] = region
        
        # if PHPSDK_CRED_PROVIDER is not None:
        #    self.__AWS_OPTIONS['credentials'] = PHPSDK_CRED_PROVIDER
        # elif PHPSDK_CRED_PROFILE is not None:
        #    self.__AWS_OPTIONS['profile'] = PHPSDK_CRED_PROFILE
        
if __name__ == "__main__":
    Config.init()
    Config.set('_AWS_OPTIONS', {'signature': 'ok'})
    r = 'ap-southeast-1'
    o = Service(r)