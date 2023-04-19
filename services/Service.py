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
        
    def setRules(self, rules):
        rules = rules.lower().split('^')
        Config.set(self.RULESPREFIX, rules)
        
    def setTags(self, tags):
        rawTags = []
        if not tags:
            return
        
        result = []
        t = tags.split(self.TAGS_SEPARATOR)
        for tag in t:
            k, v = tag.split(self.KEYVALUE_SEPARATOR)
            rawTags = {k: v.split(self.VALUES_SEPARATOR) for k, v in tag.items()}
            result.append({"Name": "tag:" + k, "Values": v.split(self.VALUES_SEPARATOR)})
        
        self._tags = rawTags
        self.tags = result
        
    def __del__(self):
        Config.set(self.RULESPREFIX, [])
        
    def resourceHasTags(self, tags):
        if not self._tags:
            return True
        
        if not tags:
            return False
        
        formattedTags = {}
        for tag in tags:
            formattedTags[tag['Key']] = tag['Value']
        
        filteredTags = self._tags
        
        for key, value in filteredTags.items():
            if key not in formattedTags:
                return False
            
            cnt = 0
            for val in value:
                if formattedTags[key] == val:
                    cnt += 1
                    break
            
            if cnt == 0:
                return False
        
        return True    

if __name__ == "__main__":
    Config.init()
    Config.set('_AWS_OPTIONS', {'signature': 'ok'})
    r = 'ap-southeast-1'
    o = Service(r)