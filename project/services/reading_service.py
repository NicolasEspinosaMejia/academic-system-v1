import copy

from project.composers.external_system_compose import ExternalSystemCompose
from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils
from project.services.external_system_service import ExternalSystemService
from project.services.service import Service


class ReadingService(Service):

    __DICTIONARY__ = {
        "methodName": {
            "READING_GET_ON_DEMAND": "reading_get_on_demand"
        }
    }

    def check_attributes_reading(self, reading):
        """[summary]

        Args:
            reading ([type]): [description]

        Returns:
            [type]: [description]
        """
        request_body_variable_id_key = Constants.REQUEST_BODY_VARIABLE_ID_KEY

        request_body_external_system_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_NAME_KEY
        request_body_external_system_connection_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_CONNECTION_NAME_KEY
        request_body_devices_key = "devices"

        if not isinstance(reading, dict) or\
           not GeneralsUtils.check_dictionary_property(
                request_body_external_system_name_key, reading) or\
           not GeneralsUtils.check_dictionary_property(
                request_body_external_system_connection_name_key, reading) or\
           not GeneralsUtils.check_dictionary_property(
                request_body_devices_key, reading) or\
           not GeneralsUtils.validate_list(
                reading[request_body_devices_key]):
            return False

        devices = reading[request_body_devices_key]

        for device in list(devices):
            if not GeneralsUtils.check_dictionary_property(
               "deviceId", device):
                devices.remove(device)

        if len(devices) == 0:
            return False

        if request_body_variable_id_key not in reading or not\
           isinstance(reading[request_body_variable_id_key], str):
            return False

        return True

    def check_reading_type_code(
            self,
            reading_type_code: str):
        """[summary]

        Args:
            reading_type_code (str): [description]

        Returns:
            bool: [description]
        """
        reading_type_code_separator = "."

        if not GeneralsUtils.validate_string(reading_type_code):
            return False

        if len(reading_type_code.split(reading_type_code_separator)) != 18:
            return False

        return True

    def process_element(self, reading: dict):
        """This method is used for validated and process
        element for event search in redis the externalSystem

        Args:
            data (list): receives externalSystemName, connectionName
            and devices

        Returns:
            list: the correct element for send to sqs
        """
        request_body_external_system_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_NAME_KEY
        request_body_external_system_connection_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_CONNECTION_NAME_KEY
        request_body_variable_id_key =\
            Constants.REQUEST_BODY_VARIABLE_ID_KEY

        external_system_compose = ExternalSystemCompose(
            self.compose.database_cache_repository,
            self.compose.sender_queue_service_client)
        external_system_service = ExternalSystemService(
            external_system_compose)

        external_system_name = reading[request_body_external_system_name_key]

        external_system = external_system_service.\
            get_connection_by_connection_name(
                external_system_name,
                reading[request_body_external_system_connection_name_key])

        if not self.check_attributes_reading(reading):
            raise ValueError(
                "The reading " +
                f"'{external_system_name}' does not meet the" +
                "minimum requirements")

        reading_clone = dict(reading)

        del reading_clone[request_body_external_system_name_key]
        del reading_clone[request_body_external_system_connection_name_key]

        variable_id = reading[request_body_variable_id_key]

        variable = self.compose.get_variable(variable_id)

        self.process_element_by_standard(
            external_system, reading_clone, variable)

        return external_system, reading_clone

    def process_element_by_standard(
            self,
            external_system: dict,
            reading: dict,
            variable: dict):
        """[summary]

        Args:
            external_system (dict): [description]
            reading (dict): [description]
            variable (dict): [description]

        Raises:
            ValueError: [description]
            ValueError: [description]
        """
        request_body_reading_type_code_key =\
            Constants.REQUEST_BODY_READING_TYPE_CODE_KEY
        readind_type_code_key = "readindTypeCode"
        request_body_variable_id_key =\
            Constants.REQUEST_BODY_VARIABLE_ID_KEY

        if external_system[Constants.EXTERNAL_SYSTEM_LANGUAGE_KEY] ==\
           Constants.LANGUAGE_MULTI_SPEAK_ID:
            if request_body_reading_type_code_key not in variable:
                raise ValueError(
                    "The request data " +
                    f"'{variable[request_body_variable_id_key]}' does " +
                    "not meet the minimum requirements")

            reading_type_code = variable[request_body_reading_type_code_key]

            if not self.check_reading_type_code(reading_type_code):
                raise ValueError(
                    "The request data " +
                    f"'{reading_type_code}' does not meet " +
                    "the minimum requirements")

            del reading[request_body_variable_id_key]

            reading[readind_type_code_key] = reading_type_code

    def structuring_of_readings(
            self,
            reading_request,
            structure,
            external_system):
        result = reading_request
        external_system_key = Constants.EXTERNAL_SYSTEM_KEY

        structure[external_system_key] = external_system
        result["dataCommand"] = structure

        return result

    # -------------------------------------------------------------------

    def get_on_demand(self, data: list):
        """This method used for process and validate the flow
        the reading get on demand

        Args:
            data (list): Ajustar

        Returns:
            list: Ajustar
        """
        successful_readings = []
        result = data
        method_name = "get_on_demand"
        name_service = "reading"
        request_body_readings_key = "readings"
        external_system_key = Constants.EXTERNAL_SYSTEM_KEY
        external_system_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_NAME_KEY
        connection_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_CONNECTION_NAME_KEY
        response_body_result_key = Constants.RESPONSE_BODY_RESULT_KEY
        reference = (f"{name_service}_{method_name}").upper()

        if not GeneralsUtils.check_dictionary_property(
                request_body_readings_key,
                data):
            raise KeyError(
                    "Data does not contain node " +
                    f"'{request_body_readings_key}'")

        readings_request = data[request_body_readings_key]

        if not GeneralsUtils.validate_list(readings_request):
            raise TypeError(
                "The 'readings' is not in the correct format")

        external_system_compose = ExternalSystemCompose(
            self.compose.database_cache_repository,
            self.compose.sender_queue_service_client)
        external_system_service = ExternalSystemService(
            external_system_compose)

        capability = self.__DICTIONARY__["methodName"][reference]

        for reading_request in list(readings_request):
            if not self.check_attributes(reading_request):
                readings_request.remove(reading_request)
                continue

            try:
                if not external_system_service.check_capability(
                   name=reading_request[external_system_name_key],
                   connection_name=reading_request[connection_name_key],
                   capability=capability):
                    self.compose.system_log.add(
                        message="The external system does not have the " +
                                "capability to execute the method: " +
                                f"{method_name}",
                                process="Service")
                    reading_request[response_body_result_key] = False
                    continue

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to verify " +
                            "the capabilities of an external service",
                    error=error,
                    process="Service")
                reading_request[response_body_result_key] = False
                continue

            try:
                external_system, reading_request_clone =\
                    self.process_element(reading_request)

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying process " +
                            "a requested read",
                    error=error,
                    process="Service")
                reading_request[response_body_result_key] = False
                continue

            try:
                self.compose.send_message_command(
                    reference,
                    external_system,
                    reading_request_clone)
                reading_request[
                    response_body_result_key] = True

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to send " +
                            "message to execute the command",
                    error=error,
                    process="Service")
                reading_request[response_body_result_key] = False

            reading_request_clone[external_system_key] = external_system
            reading_request_data_command = dict(reading_request)
            reading_request_data_command["dataCommand"] = reading_request_clone

            successful_readings.append(reading_request_data_command)

        self.send_progress_notification(
            successful_readings,
            copy.deepcopy(result),
            request_body_readings_key,
            reference)

        return result
