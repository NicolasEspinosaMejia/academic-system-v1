import copy

from project.composers.external_system_compose import ExternalSystemCompose
from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils
from project.services.external_system_service import ExternalSystemService
from project.services.service import Service


class ControlActionService(Service):
    """This class is in charge of executing different control actions,
       among them there is the cutting and reconnection of devices,
       which is one of the main methods that this class will have.
    """

    __DICTIONARY__ = {
        "connect": {
            "methodName": "CONTROL_ACTION_CONNECT",
            "capability": "control_action_connect_disconnect"
        },
        "disconnect": {
            "methodName": "CONTROL_ACTION_DISCONNECT",
            "capability": "control_action_connect_disconnect"
        }
    }

    def check_attributes_control_action(self, control_action):
        """[summary]

        Args:
            reading ([type]): [description]

        Returns:
            [type]: [description]
        """
        request_body_action_key = "action"

        result = self.check_attributes(control_action)

        if result is False:
            return result

        if request_body_action_key not in control_action or\
           control_action[request_body_action_key] not in\
           self.__DICTIONARY__:
            return False

        return True

    def process_element(self, control_action: dict):
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
        request_body_action_key = "action"

        external_system_compose = ExternalSystemCompose(
            self.compose.database_cache_repository,
            self.compose.sender_queue_service_client)
        external_system_service = ExternalSystemService(
            external_system_compose)

        external_system_name =\
            control_action[request_body_external_system_name_key]

        external_system = external_system_service.\
            get_connection_by_connection_name(
                external_system_name,
                control_action[
                    request_body_external_system_connection_name_key])

        if not external_system_service.check_attributes_external_system(
                external_system):
            raise ValueError(
                "The event " +
                f"'{external_system_name}' does not meet the" +
                "minimum requirements")

        control_action_clone = dict(control_action)

        del control_action_clone[request_body_external_system_name_key]
        del control_action_clone[
            request_body_external_system_connection_name_key]
        del control_action_clone[request_body_action_key]

        return external_system, control_action_clone

    # -------------------------------------------------------------------

    def execute(self, data: dict):
        """This method is in charge of executing the control actions,
           as the case may be.

        Args:
            data (dict): This component is a dictionary that is made
                         up of control actions

        Returns:
            list: This method returns a list of already validated
            control actions, which will be identified with a true
            or false according to the validation case they have had.
        """
        successful_readings = []
        result = data
        name_service = "control_action"
        name_method = "execute"
        request_control_actions_key = "controlActions"
        request_control_action_action_key = "action"
        external_system_key = Constants.EXTERNAL_SYSTEM_KEY
        external_system_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_NAME_KEY
        connection_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_CONNECTION_NAME_KEY
        response_body_result_key = Constants.RESPONSE_BODY_RESULT_KEY
        reference = (f"{name_service}_{name_method}").upper()

        if not GeneralsUtils.check_dictionary_property(
                request_control_actions_key,
                data):
            raise KeyError(
                    "Data does not contain node " +
                    f"'{request_control_actions_key}'")

        control_actions_request = data[request_control_actions_key]

        if not GeneralsUtils.validate_list(control_actions_request):
            raise TypeError(
                "The 'control_actions' is not in the correct format")

        external_system_compose = ExternalSystemCompose(
            self.compose.database_cache_repository,
            self.compose.sender_queue_service_client)
        external_system_service = ExternalSystemService(
            external_system_compose)

        for control_action_request in list(control_actions_request):
            if not self.check_attributes_control_action(
                    control_action_request):
                control_actions_request.remove(control_action_request)
                continue

            definition =\
                self.__DICTIONARY__[control_action_request[
                    request_control_action_action_key]]

            capability = definition["capability"]

            try:
                if not external_system_service.check_capability(
                   name=control_action_request[external_system_name_key],
                   connection_name=control_action_request[connection_name_key],
                   capability=capability):
                    self.compose.system_log.add(
                        message="The external system does not have the " +
                                "capability to execute the method: " +
                                f"{capability}",
                                process="Service")
                    control_action_request[response_body_result_key] = False
                    continue

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to verify " +
                            "the capabilities of an external service",
                    error=error,
                    process="Service")
                control_action_request[response_body_result_key] = False
                continue

            try:
                external_system, control_action_request_clone =\
                    self.process_element(control_action_request)

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying process " +
                            "a requested read",
                    error=error,
                    process="Service")
                control_action_request[response_body_result_key] = False
                continue

            try:
                self.compose.send_message_command(
                    definition["methodName"],
                    external_system,
                    control_action_request_clone)
                control_action_request[
                    response_body_result_key] = True

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to send " +
                            "message to execute the command",
                    error=error,
                    process="Service")
                control_action_request[response_body_result_key] = False

            control_action_request_clone[external_system_key] = external_system
            control_action_request_data_command = dict(control_action_request)
            control_action_request_data_command["dataCommand"] =\
                control_action_request_clone

            successful_readings.append(control_action_request_data_command)

        self.compose.send_progress_notification(
            successful_readings,
            copy.deepcopy(result),
            request_control_actions_key,
            reference)

        return result
