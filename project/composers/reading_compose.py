from project.constants import Constants
from project.composers.compose import Compose
from project.configuration_manager import ConfigurationManager
from project.models.queue_message_model import QueueMessageModel
from project.resources.utils.queue_service_utils import QueueServiceUtils
from project.resources.utils.generals_utils import GeneralsUtils


class ReadingCompose(Compose):

    def get_variable(self, variable_id: str) -> str:
        result = {}

        if not GeneralsUtils.validate_string(variable_id):
            raise TypeError(
                "The 'variable_id' is not in the correct format")

        database_cache_reading_type_code_key =\
            ConfigurationManager.get_database_cache_key(
                "VARIABLE").format(variable_id)

        result = self.get_database_cache_value(
            database_cache_reading_type_code_key)

        if result is None or len(result) == 0:
            raise ValueError(
                f"No variable {variable_id} data found in the cache database")

        return result

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
        request_body_external_system_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_NAME_KEY

        external_system_language = Constants.LANGUAGE_PRIME_ANALYTICS_PLUS_ID
        external_system_version = Constants.TYPE_REFERENCE_PRIME_ANALYTICS_PLUS

        queue_message_event_type =\
            QueueServiceUtils.get_message_event_type_by_method_name(
                    external_system_language,
                    external_system_version,
                    reference)

        component = Constants.QUEUE_MESSAGE_SOURCE_VALUE

        elements_success = 0
        total_elements = 0
        register = 0

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
            total_elements = total_elements + len(item["devices"])

            if item["result"]:
                elements_success += len(item["devices"])

            external_system_name =\
                item[request_body_external_system_name_key]
            data_readings =\
                (list(filter(lambda x:
                             x[request_body_external_system_name_key] ==
                             external_system_name,
                             successful_readings)))

            if len(data_readings) != 0:
                queue_message_data["value"][name_service][register] =\
                    data_readings[0]

            else:
                queue_message_data["value"][name_service][register]["dataCommand"] =\
                    {}

            queue_message_data["value"][name_service][register]["totalDevices"] =\
                len(item["devices"])

            register = register + 1

        queue_message_data["value"]["totalDevices"] = total_elements
        queue_message_data["value"]["success"] = 0
        queue_message_data["value"]["error"] =\
            queue_message_data["value"]["totalDevices"] - elements_success

        self.sender_queue_service_client.send_message(
            ConfigurationManager.get_config("QUEUE_PARAMETER_NAME"),
            QueueMessageModel(
                "fun-parameter",
                queue_message_event_type,
                [queue_message_data]))
