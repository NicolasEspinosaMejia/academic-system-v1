
import copy

from project.composers.external_system_compose import ExternalSystemCompose
from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils
from project.services.external_system_service import ExternalSystemService
from project.services.service import Service


class MeteringSystemService(Service):

    def check_external_systems_attribute(
            self,
            data):
        request_body_external_systems_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEMS_KEY

        if not GeneralsUtils.check_dictionary_property(
           request_body_external_systems_key,
           data):
            return False

        if not GeneralsUtils.validate_list(
                data[request_body_external_systems_key]):
            return False

        return True

    # -------------------------------------------------------------------

    def discover(self, data: dict):
        metering_system_request_data_command = {}
        successful_topology = []
        result = data
        external_system_key = Constants.EXTERNAL_SYSTEM_KEY
        request_metering_systems_key = "externalSystems"
        method_name = "METERING_SYSTEM_DISCOVER"
        external_system_name_key = Constants.EXTERNAL_SYSTEM_NAME_KEY
        external_system_connection_name_key =\
            Constants.EXTERNAL_SYSTEM_CONNECTION_NAME_KEY
        response_body_result_key = Constants.RESPONSE_BODY_RESULT_KEY

        if not self.check_external_systems_attribute(data):
            raise ValueError(
                "The 'data' are not in the correct format")

        external_systems_request = data[
            Constants.REQUEST_BODY_EXTERNAL_SYSTEMS_KEY]

        external_system_compose = ExternalSystemCompose(
            self.compose.database_cache_repository,
            self.compose.sender_queue_service_client)
        external_system_service = ExternalSystemService(
            external_system_compose)

        for external_system_request in list(external_systems_request):
            if not isinstance(external_system_request, dict):
                external_systems_request.remove(external_system_request)
                continue

            if external_system_name_key not in external_system_request or\
               external_system_connection_name_key not in\
               external_system_request:
                external_systems_request.remove(external_system_request)
                continue

            external_system_name = external_system_request[
                    Constants.EXTERNAL_SYSTEM_NAME_KEY]
            connection_name = external_system_request[
                    Constants.EXTERNAL_SYSTEM_CONNECTION_NAME_KEY]

            try:
                if not external_system_service.check_capability(
                   name=external_system_name,
                   connection_name=connection_name,
                   capability=method_name.lower()):
                    external_system_request[
                        response_body_result_key] = False
                    self.compose.system_log.add(
                        message="The external system " +
                                f"{external_system_name} does not have the " +
                                "capability to execute the method: " +
                                f"{method_name}",
                                process="Service")
                    continue

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to verify " +
                            "the capabilities of an external system",
                    error=error,
                    process="Service")
                external_system_request[
                    response_body_result_key] = False
                continue

            try:
                external_system =\
                    external_system_service.get_connection_by_connection_name(
                        external_system_name,
                        connection_name)

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to query " +
                            "a connection from an external system",
                    error=error,
                    process="Service")
                external_system_request[
                    response_body_result_key] = False
                continue

            try:
                self.compose.send_message_command(
                    method_name,
                    external_system)
                external_system_request[
                    response_body_result_key] = True

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to send " +
                            "message to execute the command",
                    error=error,
                    process="Service")
                external_system_request[
                    response_body_result_key] = False

            metering_system_request_data_command[external_system_key] =\
                external_system
            metering_system_request_data_command["dataCommand"] =\
                external_system_request

            successful_topology.append(metering_system_request_data_command)

        self.compose.send_progress_notification(
            successful_topology,
            copy.deepcopy(result),
            request_metering_systems_key,
            method_name)

        return result
