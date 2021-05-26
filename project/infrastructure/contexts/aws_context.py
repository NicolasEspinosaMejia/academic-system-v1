import boto3

from project.adapters.middlerware_adapter import MiddlerwareAdapter
from project.configuration_manager import ConfigurationManager
from project.constants import Constants


class AwsContextWithSession(MiddlerwareAdapter):

    session_queue_service_client = None

    def __init__(self):
        aws_sqs_access_key_id =\
            ConfigurationManager.get_config("AWS_SQS_ACCESS_KEY_ID")
        aws_sqs_secret_access_key =\
            ConfigurationManager.get_config("AWS_SQS_SECRET_ACCESS_KEY")
        aws_sqs_region_name =\
            ConfigurationManager.get_config("AWS_SQS_REGION_NAME")
        self.session_queue_service_client = self.__build_session(
            access_key_id=aws_sqs_access_key_id,
            secret_access_key=aws_sqs_secret_access_key,
            region_name=aws_sqs_region_name)

    def __build_session(
            self,
            access_key_id,
            secret_access_key,
            region_name):
        return boto3.Session(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region_name)

    def get_queue_service_client(self):
        resource_sqs =\
            self.session_queue_service_client.resource(
                Constants.SQS_RESOURCE_NAME)
        return resource_sqs


class AwsContextWithoutSession(MiddlerwareAdapter):

    __queue_service_client__ = None

    def __init__(self):
        self.__queue_service_client__ =\
            boto3.client(Constants.SQS_RESOURCE_NAME)

    def get_queue_service_client(self):
        return self.__queue_service_client__
