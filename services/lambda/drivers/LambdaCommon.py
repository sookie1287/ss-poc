import json
import os
from datetime import datetime, timedelta

import boto3

class LambdaCommon:
    RUNTIME_PREFIX = [
        'nodejs',
        'python',
        'java',
        'dotnetcore',
        'dotnet',
        'go',
        'ruby'
    ]

    CUSTOM_RUNTIME_PREFIX = [
        'provided'
    ]

    RUNTIME_PATH = os.path.join(os.environ.get("VENDOR_DIR"), 'aws/aws-sdk-php/src/data/lambda/2015-03-31/api-2.json.php')
    CW_HISTORY_DAYS = [30, 7]

    def __init__(self, lambda_, lambda_client, iam_client, role_count):
        self.lambda_ = lambda_
        self.function_name = lambda_['FunctionName']
        self.role_count = role_count
        self.lambda_client = lambda_client
        self.iam_client = iam_client
        self.results = {}
        self.init()

    def init(self):
        self.__check_function_url_in_used()
        self.__check_missing_role()
        self.__check_url_without_auth()
        self.__check_code_signing_disabled()
        self.__check_dead_letter_queue_disabled()
        self.__check_env_var_default_key()
        self.__check_enhanced_monitor()
        self.__check_provisioned_concurrency()
        self.__check_tracing_enabled()
        self.__check_role_reused()
        self.__check_runtime()
        self.__check_function_in_used()

    def __check_function_url_in_used(self):
        url_config = self.lambda_client.list_function_url_configs(
            FunctionName=self.function_name
        )
        if url_config['FunctionUrlConfigs']:
            self.results['lambdaURLInUsed'] = [-1, "Enabled"]
        return

    def __check_missing_role(self):
        role_arn = self.lambda_['Role']
        role_name = self.get_arn_role_name(role_arn)

        try:
            role = self.iam_client.get_role(
                RoleName=role_name
            )
        except boto3.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                self.results['lambdaMissingRole'] = [-1, '']
            else:
                raise e
        return

    @staticmethod
    def get_arn_role_name(arn):
        array = arn.split("/")
        role_name = array[-1]
        return role_name

    def __check_url_without_auth(self):
        url_configs = self.lambda_client.list_function_url_configs(
            FunctionName=self.function_name
        )

        if url_configs['FunctionUrlConfigs']:
            for config in url_configs['FunctionUrlConfigs']:
                if config['AuthType'] == 'NONE':
                    self.results['lambdaURLWithoutAuth'] = [-1, config['AuthType']]
                    return

        return

    def __check_code_signing_disabled(self):
        code_sign = self.lambda_client.get_function_code_signing_config(
            FunctionName=self.function_name
        )
        if not code_sign.get('CodeSigningConfigArn'):
            self.results['lambdaCodeSigningDisabled'] = [-1, 'Disabled']

        return

    def __check_dead_letter_queue_disabled(self):
        config = self.lambda_client.get_function_configuration(
            FunctionName=self.function_name
        )

        if not config.get('DeadLetterConfig'):
            self.results['lambdaDeadLetterQueueDisabled'] = [-1, 'Disabled']

        return

    def __check_env_var_default_key(self):
        function_name = self.lambda_['FunctionName']
        if not self.lambda_.get('KMSKeyArn'):
            self.results['lambdaCMKEncryptionDisabled'] = [-1, 'Disabled']
        return

    def __check_enhanced_monitor(self):
        if 'Layers' in self.lambda_:
            layers = self.lambda_['Layers']
            for layer in layers:
                if 'LambdaInsightsExtension' in layer['Arn']:
                    return

        self.results['lambdaEnhancedMonitoringDisabled'] = [-1, 'Disabled']
        return

    def __check_provisioned_concurrency(self):
        concurrency = self.lambda_client.get_function_concurrency(
            FunctionName=self.function_name
        )

        if not concurrency.get('ReservedConcurrentExecutions'):
            self.results['lambdaReservedConcurrencyDisabled'] = [-1, 'Disabled']

        return

    def __check_tracing_enabled(self):
        if 'TracingConfig' in self.lambda_ and 'Mode' in self.lambda_['TracingConfig'] and self.lambda_['TracingConfig']['Mode'] == 'PassThrough':
            self.results['lambdaTracingDisabled'] = [-1, 'Disabled']

        return

    def __check_role_reused(self):
        if self.role_count[self.lambda_['Role']] > 1:
            self.results['lambdaRoleReused'] = [-1, self.lambda_['Role']]
        return

    def __check_runtime(self):
        if not os.path.exists(self.RUNTIME_PATH):
            print("Skipped runtime version check due to unable to locate runtime option path")
            return

        with open(self.RUNTIME_PATH, 'r') as f:
            arr = json.load(f)

        runtime = self.lambda_['Runtime']

        runtime_prefix = ''
        runtime_version = ''

        for prefix in self.CUSTOM_RUNTIME_PREFIX:
            if runtime.startswith(prefix):
                return

        for prefix in self.RUNTIME_PREFIX:
            if runtime.startswith(prefix):
                runtime_prefix = prefix

                replace_arr = [runtime_prefix]
                if prefix in ['go', 'nodejs']:
                    replace_arr.append('.x')
                if prefix == 'nodejs':
                    replace_arr.append('-edge')

                runtime_version = runtime
                for item in replace_arr:
                    runtime_version = runtime_version.replace(item, '')
                break

        for option in arr['shapes']['Runtime']['enum']:
            if not option.startswith(runtime_prefix):
                continue
            else:
                option_version = option
                for item in replace_arr:
                    option_version = option_version.replace(item, '')
                if option_version == '':
                    option_version = 0

                if int(option_version) > int(runtime_version):
                    self.results['lambdaRuntimeUpdate'] = [-1, runtime]
                    return

        return

    def get_invocation_count(self, day):
        cw_client = boto3.client('cloudwatch')

        dimensions = [
            {
                'Name': 'FunctionName',
                'Value': self.function_name
            }
        ]

        results = cw_client.get_metric_statistics(
            Dimensions=dimensions,
            Namespace='AWS/Lambda',
            MetricName='Invocations',
            StartTime=datetime.utcnow() - timedelta(days=day),
            EndTime=datetime.utcnow(),
            Period=day * 24 * 60 * 60,
            Statistics=['SampleCount']
        )

        if not results['Datapoints']:
            return 0
        else:
            for result in results['Datapoints']:
                return result['SampleCount']

    def __check_function_in_used(self):
        for day in self.CW_HISTORY_DAYS:
            cnt = self.get_invocation_count(day)

            if cnt == 0:
                self.results['lambdaNotInUsed' + str(day) + 'Days'] = [-1, '']
                return

        return

