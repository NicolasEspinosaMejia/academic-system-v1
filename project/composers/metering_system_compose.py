from project.constants import Constants
from project.configuration_manager import ConfigurationManager
from project.models.queue_message_model import QueueMessageModel
from project.resources.utils.generals_utils import GeneralsUtils
from project.resources.utils.queue_service_utils import QueueServiceUtils
from project.composers.compose import Compose


class MeteringSystemCompose(Compose):

    def send_progress_notification(
            self,
            successful_readings: list,
            data: dict,
            name_service: str,
            reference: str):
        """This method is responsible for structuring a data to send to the
           lambda parameter, in order to store in redis

        Args:
            successful_readings (list): This attribute refers to a list of
                                        reads that passed all validation
                                        filters successfully
            data (dict, optional): This attribute refers to the data that
                                   will be stored in redis after the
                                   validations.
        """
        data = data or {}
        queue_message_data = {}

        external_system_language = Constants.LANGUAGE_PRIME_ANALYTICS_PLUS_ID
        external_system_version = Constants.TYPE_REFERENCE_PRIME_ANALYTICS_PLUS

        queue_message_event_type =\
            QueueServiceUtils.get_message_event_type_by_method_name(
                    external_system_language,
                    external_system_version,
                    reference)

        component = Constants.QUEUE_MESSAGE_SOURCE_VALUE

        wrong_elements = 0

        if not isinstance(successful_readings, list):
            raise TypeError(
                "The 'successful_readings' is not in the correct format")

        if not isinstance(data, dict):
            raise TypeError(
                "The 'data' is not in the correct format")

        if not isinstance(name_service, str):
            raise TypeError(
                "The 'name_service' is not in the correct format")

        if not isinstance(reference, str):
            raise TypeError(
                "The 'reference' is not in the correct format")

        queue_message_data["key"] = GeneralsUtils.get_global_data(
            Constants.GLOBAL_DATA_TRANSACTION_ID_KEY)
        queue_message_data["value"] = data
        queue_message_data["value"]["component"] = component

        for item in list(queue_message_data["value"][name_service]):
            if not item["result"]:
                wrong_elements = wrong_elements + 1

        total_elements = len(queue_message_data["value"][name_service])
        queue_message_data["value"]["totalServicePoints"] = total_elements
        queue_message_data["value"]["success"] = 0
        queue_message_data["value"]["error"] = wrong_elements

        self.sender_queue_service_client.send_message(
            ConfigurationManager.get_config("QUEUE_PARAMETER_NAME"),
            QueueMessageModel(
                "fun-parameter",
                queue_message_event_type,
                [queue_message_data]))
