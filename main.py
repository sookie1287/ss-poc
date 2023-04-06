from utils.Config import Config
from utils.ArguParser import ArguParser
import constants as _C

_cli_options = ArguParser.Load()

debugFlag = _cli_options['debug']
# feedbackFlag = _cli_options['feedback']
testmode = _cli_options['test']
bucket = _cli_options['bucket']
runmode = _cli_options['mode']
filters = _cli_options['filters']

DEBUG = True if debugFlag in _C.CLI_TRUE_KEYWORD_ARRAY or debugFlag is True else False
# feedbackFlag = True if feedbackFlag in _C.CLI_TRUE_KEYWORD_ARRAY or feedbackFlag is True else False
testmode = True if testmode in _C.CLI_TRUE_KEYWORD_ARRAY or testmode is True else False

runmode = runmode if runmode in ['api-raw', 'api-full', 'report'] else 'report'

# <TODO>, yet to convert to python
# S3 upload specific variables 
# uploadToS3 = Uploader.getConfirmationToUploadToS3(bucket)

# <TODO> analyse the impact profile switching
profile = _cli_options['profile']
if profile:
    global PHPSDK_CRED_PROFILE
    PHPSDK_CRED_PROFILE = profile

_AWS_OPTIONS = {
    'signature_version': Config.AWS_SDK['signature_version']
}

Config.init()
Config.set('_AWS_OPTIONS', _AWS_OPTIONS)
oo = Config.get('_AWS_OPTIONS')

# print(_cli_options['region'])


import importlib.util
ServiceClass = getattr(importlib.import_module('services.iam.Iam'), 'Iam')
o = ServiceClass(_cli_options['region'])
o.advise()
