import json
import time

from project.adapters.queue_service_client_adapter import\
    HandlerQueueServiceClientAdapter,\
    SenderQueueServiceClientAdapter
from project.configuration_manager import ConfigurationManager
from project.constants import Constants
from project.logs.system_log import SystemLog
from project.models.queue_message_model import QueueMessageModel
from project.resources.utils.generals_utils import GeneralsUtils
from project.resources.utils.queue_service_utils import QueueServiceUtils


class HandlerSqsClientWithAwsSession(HandlerQueueServiceClientAdapter):

    queue = None

    def __init__(self, middlerware_adapter, processors):
        client = middlerware_adapter.get_queue_service_client()
        try:
            self.queue = client.get_queue_by_name(
                QueueName=ConfigurationManager.get_config(
                    "QUEUE_INTEROPERABILITY_NAME"))

        except Exception as error:
            SystemLog.add(
                message="Failed to instantiate queue service handler client",
                error=error,
                business_process_id="Unknown",
                process="Initial setup")
        self.__processors = processors

    def process_message(self, message):
        queue_message_event_type_key =\
            Constants.QUEUE_MESSAGE_EVENT_TYPE_KEY
        queue_message_data_key =\
            Constants.QUEUE_MESSAGE_DATA_KEY

        if not QueueServiceUtils.\
           check_message_event_type(message):
            raise ValueError(
                f"The '{queue_message_event_type_key}' of the message " +
                "does not meet the requested requirements")

        event_type_splitted = QueueServiceUtils.split_message_event_type(
            message[queue_message_event_type_key])

        process_name = event_type_splitted[2]
        action_name = event_type_splitted[3]

        if not QueueServiceUtils.\
           check_message_attributes(message):
            raise AttributeError(
                "the message did not meet the set attribute requirements")

        QueueServiceUtils.set_global_data_attributes(message)

        if queue_message_data_key not in message:
            raise AttributeError(
                f"Failed to get attribute '{queue_message_data_key}' " +
                "from message body")

        message_data = message[queue_message_data_key]

        if not isinstance(message_data, list):
            raise TypeError(
                "The 'data' is not in the correct format")

        if len(message_data) == 0:
            raise ValueError("There is no 'data' in the body of the message")

        if process_name not in self.__processors:
            raise ValueError("The process name was not set in the system")

        processor = self.__processors[process_name]

        if not hasattr(processor, action_name):
            raise AttributeError("Method name was not set on the system")

        processor_method = getattr(processor, action_name)
        result = processor_method(message_data)

        return result

    def receive_message(self):
        while True:
            sqs_messages = []
            try:
                if self.queue is None:
                    continue

                sqs_messages = self.queue.receive_messages(
                    WaitTimeSeconds=1)

            except Exception as error:
                SystemLog.add(
                    message="The message from the queue " +
                            "could not be processed",
                    error=error,
                    business_process_id="Unknown",
                    process="Receive message")
                time.sleep(5)
                continue

            if len(sqs_messages) == 0:
                continue

            for sqs_message in sqs_messages:
                result = None
                try:
                    message = self.get_message_from_sqs_message(sqs_message)
                    result = self.process_message(message)

                except Exception as error:
                    self.report_sqs_message_error(sqs_message, error)
                    continue

                if result:
                    sqs_message.delete()

    def get_message_from_sqs_message(self, sqs_message):
        sqs_message_body_key = "body"

        if not hasattr(
           sqs_message,
           sqs_message_body_key):
            raise AttributeError(
                "The message does not contain the " +
                f"'{sqs_message_body_key}' attribute")

        sqs_message_body =\
            getattr(sqs_message, sqs_message_body_key)

        message = json.loads(sqs_message_body)

        return message

    def report_sqs_message_error(self, sqs_message, error):
        sqs_message_message_property_name =\
            Constants.SQS_MESSAGE_MESSAGE_PROPERTY_NAME
        business_process_id = None
        if hasattr(
                sqs_message,
                sqs_message_message_property_name):
            business_process_id =\
                getattr(
                    sqs_message,
                    sqs_message_message_property_name)

        SystemLog.add(
            message="The message from the queue " +
                    "could not be processed",
            error=error,
            business_process_id=business_process_id,
            process="Receive message")


class HandlerSqsClientWithoutAwsSession(HandlerQueueServiceClientAdapter):

    queue_url = None

    def __init__(self, middlerware_adapter, processors):
        self.client = middlerware_adapter.get_queue_service_client()
        try:
            self.queue_url = self.get_queue_url(
                ConfigurationManager.get_config(
                    "QUEUE_INTEROPERABILITY_NAME"))

        except Exception as error:
            SystemLog.add(
                message="Failed to instantiate queue service handler client",
                error=error,
                business_process_id="Unknown",
                process="Initial setup")
        self.__processors = processors

    def get_message_from_sqs_message(self, sqs_message):
        sqs_message_body_key = "Body"

        if sqs_message_body_key not in sqs_message:
            raise AttributeError(
                "The message does not contain the " +
                f"'{sqs_message_body_key}' attribute")

        sqs_message_body =\
            sqs_message[sqs_message_body_key]

        message = json.loads(sqs_message_body)

        return message

    def get_queue_url(self, queue_name):
        return self.client.get_queue_url(QueueName=queue_name)["QueueUrl"]

    def process_message(self, message):
        queue_message_event_type_key =\
            Constants.QUEUE_MESSAGE_EVENT_TYPE_KEY
        queue_message_data_key =\
            Constants.QUEUE_MESSAGE_DATA_KEY

        if not QueueServiceUtils.\
           check_message_event_type(message):
            raise ValueError(
                f"The '{queue_message_event_type_key}' of the message " +
                "does not meet the requested requirements")

        event_type_splitted = QueueServiceUtils.split_message_event_type(
            message[queue_message_event_type_key])

        process_name = event_type_splitted[2]
        action_name = event_type_splitted[3]

        if not QueueServiceUtils.\
           check_message_attributes(message):
            raise AttributeError(
                "the message did not meet the set attribute requirements")

        QueueServiceUtils.set_global_data_attributes(message)

        if queue_message_data_key not in message:
            raise AttributeError(
                f"Failed to get attribute '{queue_message_data_key}' " +
                "from message body")

        message_data = message[queue_message_data_key]

        if not isinstance(message_data, list):
            raise TypeError(
                "The 'data' is not in the correct format")

        if len(message_data) == 0:
            raise ValueError("There is no 'data' in the body of the message")

        if process_name not in self.__processors:
            raise ValueError("The process name was not set in the system")

        processor = self.__processors[process_name]

        if not hasattr(processor, action_name):
            raise AttributeError("Method name was not set on the system")

        processor_method = getattr(processor, action_name)
        result = processor_method(message_data)

        return result

    def receive_message(self):
        while True:
            sqs_messages = []
            try:
                if self.queue_url is None:
                    continue

                sqs_messages = self.client.receive_message(
                    QueueUrl=self.queue_url,
                    WaitTimeSeconds=1)

            except Exception as error:
                SystemLog.add(
                    message="The message from the queue " +
                            "could not be processed",
                    error=error,
                    business_process_id="Unknown",
                    process="Receive message")
                time.sleep(5)
                continue

            if "Messages" not in sqs_messages:
                continue

            sqs_messages = sqs_messages["Messages"]

            for sqs_message in sqs_messages:
                result = None
                try:
                    message = self.get_message_from_sqs_message(sqs_message)
                    result = self.process_message(message)

                except Exception as error:
                    self.report_sqs_message_error(sqs_message, error)
                    continue

                if result:
                    sqs_message.delete()

    def report_sqs_message_error(self, sqs_message, error):
        sqs_message_message_property_name =\
            Constants.SQS_MESSAGE_MESSAGE_PROPERTY_NAME
        business_process_id = None
        if hasattr(
                sqs_message,
                sqs_message_message_property_name):
            business_process_id =\
                getattr(
                    sqs_message,
                    sqs_message_message_property_name)

        SystemLog.add(
            message="The message from the queue " +
                    "could not be processed",
            error=error,
            business_process_id=business_process_id,
            process="Receive message")


class SenderSqsClientWithAwsSession(SenderQueueServiceClientAdapter):

    def __init__(self, middlerware_adapter):
        self.client = middlerware_adapter.get_queue_service_client()

    def get_queue_by_name(self, queue_name):
        return self.client.get_queue_by_name(QueueName=queue_name)

    def send_message(
            self,
            queue_target_name: str,
            queue_message: QueueMessageModel):
        if not GeneralsUtils.validate_string(queue_target_name):
            raise TypeError(
                "The 'queue_target_name' is not in the correct format")

        elif not isinstance(queue_message, QueueMessageModel):
            raise TypeError(
                "The 'queue_message' is not in the correct format")

        queue = self.get_queue_by_name(queue_target_name)
        queue.send_message(
            MessageBody=json.dumps(queue_message.to_dict()))


class SenderSqsClientWithoutAwsSession(SenderQueueServiceClientAdapter):

    def __init__(self, middlerware_adapter):
        self.client = middlerware_adapter.get_queue_service_client()

    def get_queue_url(self, queue_name):
        return self.client.get_queue_url(QueueName=queue_name)

    def send_message(
            self,
            queue_target_name: str,
            queue_message: QueueMessageModel):
        if not GeneralsUtils.validate_string(queue_target_name):
            raise TypeError(
                "The 'queue_target_name' is not in the correct format")

        elif not isinstance(queue_message, QueueMessageModel):
            raise TypeError(
                "The 'queue_message' is not in the correct format")

        queue_url = self.get_queue_url(queue_target_name)["QueueUrl"]
        self.client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(queue_message.to_dict()))
