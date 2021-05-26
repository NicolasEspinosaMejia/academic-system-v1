from project.composers.external_system_compose import ExternalSystemCompose
from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils
from project.services.external_system_service import ExternalSystemService
from project.services.service import Service


class EventService(Service):

    def check_attributes_event(self, event):
        """[summary]

        Args:
            reading ([type]): [description]

        Returns:
            [type]: [description]
        """
        return self.check_attributes(event)

    def process_element(self, event: dict):
        """[summary]

        Args:
            reading (dict): [description]

        Raises:
            ValueError: [description]
            ValueError: [description]

        Returns:
            [type]: [description]
        """
        request_body_external_system_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_NAME_KEY
        request_body_external_system_connection_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_CONNECTION_NAME_KEY

        external_system_compose = ExternalSystemCompose(
            self.compose.database_cache_repository,
            self.compose.sender_queue_service_client)
        external_system_service = ExternalSystemService(
            external_system_compose)

        external_system_name = event[request_body_external_system_name_key]

        external_system = external_system_service.\
            get_connection_by_connection_name(
                external_system_name,
                event[request_body_external_system_connection_name_key])

        if not external_system_service.check_attributes_external_system(
                external_system):
            raise ValueError(
                "The event " +
                f"'{external_system_name}' does not meet the" +
                "minimum requirements")

        event_clone = dict(event)

        del event_clone[request_body_external_system_name_key]
        del event_clone[request_body_external_system_connection_name_key]

        return external_system, event_clone

    # -------------------------------------------------------------------

    def subscribe(self, data: dict) -> list:
        """The requester asks the receiver to start monitoring the events
       of a set of meters

        Args:
            data (dict): data received from view with list of events
                         that have externalSystemName, connectionName
                         and deviceIds

        Returns:
            list: Ajustar
        """
        """This method used for process and validate the flow
        the reading get on demand

        Args:
            data (list): Ajustar

        Returns:
            list: Ajustar
        """
        result = data
        method_name = "EVENT_SUBSCRIBE"
        request_body_events_key = "events"
        external_system_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_NAME_KEY
        connection_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_CONNECTION_NAME_KEY
        response_body_result_key = Constants.RESPONSE_BODY_RESULT_KEY

        if not GeneralsUtils.check_dictionary_property(
                request_body_events_key,
                data):
            raise KeyError(
                    "Data does not contain node " +
                    f"'{request_body_events_key}'")

        events_request = data[request_body_events_key]

        if not GeneralsUtils.validate_list(events_request):
            raise TypeError(
                "The 'readings' is not in the correct format")

        external_system_compose = ExternalSystemCompose(
            self.compose.database_cache_repository,
            self.compose.sender_queue_service_client)
        external_system_service = ExternalSystemService(
            external_system_compose)

        for event_request in list(events_request):
            if not self.check_attributes_event(
                    event_request):
                events_request.remove(event_request)
                continue

            try:
                if not external_system_service.check_capability(
                   name=event_request[external_system_name_key],
                   connection_name=event_request[connection_name_key],
                   capability=method_name):
                    self.compose.system_log.add(
                        message="The external system does not have the " +
                                "capability to execute the method: " +
                                f"{method_name}",
                                process="Service")
                    event_request[response_body_result_key] = False
                    continue

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to verify " +
                            "the capabilities of an external service",
                    error=error,
                    process="Service")
                event_request[response_body_result_key] = False
                continue

            try:
                external_system, event_request_clone =\
                    self.process_element(event_request)

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying process " +
                            "a requested read",
                    error=error,
                    process="Service")
                event_request[response_body_result_key] = False
                continue

            try:
                self.compose.send_message_command(
                    method_name,
                    external_system,
                    event_request_clone)
                event_request[
                    response_body_result_key] = True

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to send " +
                            "message to execute the command",
                    error=error,
                    process="Service")
                event_request[response_body_result_key] = False

        return result

    def get_on_demand(self, data: dict) -> list:
        """This method used for process and validate the flow
        of the endpoint GetEndDeviceEventsByMeterIDsAndEventTypes

        Args:
            data (dict): data received from view with list of events
                         that have externalSystemName, connectionName
                         and deviceIds

        Returns:
            list: The data validate if was success of fail
        """
        result = data
        method_name = "READING_GET_ON_DEMAND"
        request_body_events_key = "events"
        external_system_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_NAME_KEY
        connection_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_CONNECTION_NAME_KEY
        response_body_result_key = Constants.RESPONSE_BODY_RESULT_KEY

        if not GeneralsUtils.check_dictionary_property(
                request_body_events_key,
                data):
            raise KeyError(
                    "Data does not contain node " +
                    f"'{request_body_events_key}'")

        events_request = data[request_body_events_key]

        if not GeneralsUtils.validate_list(events_request):
            raise TypeError(
                "The 'readings' is not in the correct format")

        external_system_compose = ExternalSystemCompose(
            self.compose.database_cache_repository,
            self.compose.sender_queue_service_client)
        external_system_service = ExternalSystemService(
            external_system_compose)

        for event_request in list(events_request):
            if not self.check_attributes_event(
                    event_request):
                events_request.remove(event_request)
                continue

            try:
                if not external_system_service.check_capability(
                   name=event_request[external_system_name_key],
                   connection_name=event_request[connection_name_key],
                   capability=method_name):
                    self.compose.system_log.add(
                        message="The external system does not have the " +
                                "capability to execute the method: " +
                                f"{method_name}",
                                process="Service")
                    event_request[response_body_result_key] = False
                    continue

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to verify " +
                            "the capabilities of an external service",
                    error=error,
                    process="Service")
                event_request[response_body_result_key] = False
                continue

            try:
                external_system, event_request_clone =\
                    self.process_element(event_request)
                if not self.validate_event_type_codes(
                        event_request_clone["eventTypeCodes"]):
                    raise ValueError

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying process " +
                            "a requested read",
                    error=error,
                    process="Service")
                event_request[response_body_result_key] = False
                continue

            try:
                self.compose.send_message_command(
                    method_name,
                    external_system,
                    event_request_clone)
                event_request[
                    response_body_result_key] = True

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to send " +
                            "message to execute the command",
                    error=error,
                    process="Service")
                event_request[response_body_result_key] = False

        return result

    def validate_event_type_codes(self, event_type_codes: list):

        result = []
        event_type_codes_cache = self.compose.get_event_type_codes()
        for item in event_type_codes:
            event_type_code_split = item.split(".")
            event_type = f"{event_type_code_split[1]}."\
                         f"{event_type_code_split[2]}."\
                         f"{event_type_code_split[3]}"

            if event_type_code_split[0] == "3" and\
               event_type in event_type_codes_cache:
                result.append(True)
            else:
                result.append(False)

        return all(result)
