from project.composers.external_system_compose import ExternalSystemCompose
from project.composers.reading_compose import ReadingCompose
from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils
from project.services.external_system_service import ExternalSystemService
from project.services.reading_service import ReadingService
from project.services.service import Service


class ScheduleService(Service):

    def check_attributes_enable(self, attributes: dict):
        """This method is in charge of validating the attributes that
           the request dictionary must contain

        Args:
            attributes (dict): Ajustar

        Returns:
            bool: Ajustar
        """
        result = True
        request_body_external_system_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_NAME_KEY
        request_body_connection_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_CONNECTION_NAME_KEY
        request_body_schedule_id_key = Constants.REQUEST_BODY_SCHEDULE_ID_KEY
        request_body_schedule_guid_key =\
            Constants.REQUEST_BODY_SCHEDULE_GUID_KEY

        if not isinstance(attributes, dict) or not\
           GeneralsUtils.check_dictionary_property(
                request_body_external_system_name_key, attributes) or not\
           GeneralsUtils.check_dictionary_property(
                request_body_connection_name_key, attributes) or not\
           GeneralsUtils.check_dictionary_property(
                request_body_schedule_id_key, attributes) or not\
           GeneralsUtils.check_dictionary_property(
                request_body_schedule_guid_key, attributes):
            result = False

        return result

    def process_element(self, schedule: dict):
        """[summary]

        Args:
            schedule (dict): [description]

        Returns:
            [type]: [description]
        """

        reading_compose = ReadingCompose(
            self.compose.database_cache_repository,
            self.compose.sender_queue_service_client)
        reading_service = ReadingService(
            reading_compose)

        external_system, reading_clone =\
            reading_service.process_element(schedule)

        schedule_clone = reading_clone

        return external_system, schedule_clone

    # -------------------------------------------------------------------

    def create_reading_schedule(self, data: list) -> list:
        """Principal method used for program reading schedule
            and send the command to sqs

        Args:
            data (list): data received from view with list of readings
        that have externalSystemName, connectionName, deviceIds,
        readingTypeCodes and schedule

        Returns:
            dict: data processed successfully and send sqs
        """
        result = data
        method_name = "SCHEDULE_CREATE_READING"
        request_body_schedules_key = "schedules"
        external_system_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_NAME_KEY
        connection_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_CONNECTION_NAME_KEY
        response_body_result_key = Constants.RESPONSE_BODY_RESULT_KEY

        if not GeneralsUtils.check_dictionary_property(
                request_body_schedules_key,
                data):
            raise KeyError(
                    "Data does not contain node " +
                    f"'{request_body_schedules_key}'")

        schedules_request = data[request_body_schedules_key]

        if not GeneralsUtils.validate_list(schedules_request):
            raise TypeError(
                "The 'readings' is not in the correct format")

        external_system_compose = ExternalSystemCompose(
            self.compose.database_cache_repository,
            self.compose.sender_queue_service_client)
        external_system_service = ExternalSystemService(
            external_system_compose)

        for schedule_request in list(schedules_request):
            if not self.check_attributes(schedule_request):
                schedules_request.remove(schedule_request)
                continue

            try:
                if not external_system_service.check_capability(
                   name=schedule_request[external_system_name_key],
                   connection_name=schedule_request[connection_name_key],
                   capability=method_name):
                    self.compose.system_log.add(
                        message="The external system does not have the " +
                                "capability to execute the method: " +
                                f"{method_name}",
                                process="Service")
                    schedule_request[response_body_result_key] = False
                    continue

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to verify " +
                            "the capabilities of an external service",
                    error=error,
                    process="Service")
                schedule_request[response_body_result_key] = False
                continue

            try:
                external_system, schedule_request_clone =\
                    self.process_element(schedule_request)

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying process " +
                            "a requested read",
                    error=error,
                    process="Service")
                schedule_request[response_body_result_key] = False
                continue

            try:
                self.compose.send_message_command(
                    method_name,
                    external_system,
                    schedule_request_clone)
                schedule_request[
                    response_body_result_key] = True

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to send " +
                            "message to execute the command",
                    error=error,
                    process="Service")
                schedule_request[response_body_result_key] = False

        return result

    def enable_reading_schedule(self, data: list) -> list:
        """Method to activate schedules of any kind

        Args:
            data (list): It contains a list in which each element is
                         made up of the jobs required to consult an
                         external system, the type of schedule and its
                         identifiers.

        Returns:
            dict: List that contains the result of the processing of
                  each schedule. If the result is true, it indicates
                  that a command is sent to request the action to an
                  external system.
        """
        result = data
        method_name = "SCHEDULE_ENABLE_READING"
        request_body_schedule_key = "schedules"
        request_body_external_system_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_NAME_KEY
        request_body_external_system_connection_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_CONNECTION_NAME_KEY
        response_body_result_key = Constants.RESPONSE_BODY_RESULT_KEY

        if not GeneralsUtils.check_dictionary_property(
                request_body_schedule_key,
                data):
            raise KeyError(
                    "Data does not contain node " +
                    f"'{request_body_schedule_key}'")

        schedules_request = data[request_body_schedule_key]

        if not GeneralsUtils.validate_list(schedules_request):
            raise TypeError(
                f"The '{request_body_schedule_key}' is not in" +
                "the correct format")

        external_system_compose = ExternalSystemCompose(
            self.compose.database_cache_repository,
            self.compose.sender_queue_service_client)
        external_system_service = ExternalSystemService(
            external_system_compose)

        for schedule_request in list(schedules_request):
            if not self.check_attributes_enable(
                    schedule_request):
                schedules_request.remove(schedule_request)
                continue

            try:
                if not external_system_service.check_capability(
                   name=schedule_request[
                        request_body_external_system_name_key],
                   connection_name=schedule_request[
                        request_body_external_system_connection_name_key],
                   capability=method_name):
                    self.compose.system_log.add(
                        message="The external system does not have the " +
                                "capability to execute the method: " +
                                f"{method_name}",
                                process="Service")
                    schedule_request[response_body_result_key] = False
                    continue

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to verify " +
                            "the capabilities of an external service",
                    error=error,
                    process="Service")
                schedule_request[response_body_result_key] = False
                continue

            try:
                external_system =\
                    external_system_service.get_connection_by_connection_name(
                        schedule_request[
                            request_body_external_system_name_key],
                        schedule_request[
                            request_body_external_system_connection_name_key])

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to query " +
                            "a connection from an external system",
                    error=error,
                    process="Service")
                schedule_request[response_body_result_key] = False
                continue

            if not external_system_service.check_attributes_external_system(
                    external_system):
                self.compose.system_log.add(
                    message="The external system does not meet the" +
                            "minimum requirements",
                    process="Service")
                schedule_request[response_body_result_key] = False
                continue

            schedule_request_clone = dict(schedule_request)

            del schedule_request_clone[
                    request_body_external_system_name_key]
            del schedule_request_clone[
                    request_body_external_system_connection_name_key]

            try:
                self.compose.send_message_command(
                    method_name,
                    external_system,
                    schedule_request_clone)
                schedule_request[
                    response_body_result_key] = True

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to send " +
                            "message to execute the command",
                    error=error,
                    process="Service")
                schedule_request[response_body_result_key] = False

        return result
