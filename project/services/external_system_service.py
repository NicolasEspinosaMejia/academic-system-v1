from project.configuration_manager import ConfigurationManager
from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils
from project.services.service import Service


class ExternalSystemService(Service):

    __DICTIONARY__ = {
        "configuration": {
            "458": "host",
            "459": "host",
            "460": "host",
            "461": "host",
            "462": "user",
            "463": "password",
            "464": "intervalSize",
            "465": "port",
            "467": "privateKeyPath",
            "698": "sourcePath",
            "719": "targetPath",
            "733": "language",
            "1": "owner"
        },
        "language": {
            "29": {
                "language": "MSP",
                "version": "5.0.0"
            },
            "30": {
                "language": "ADF",
                "version": "6.0.0"
            }
        }
    }

    def check_attributes_external_system(self, external_system):
        if not isinstance(external_system, dict):
            return False

        fail = None
        for external_system_attribute in\
                Constants.EXTERNAL_SYSTEM_ATTRIBUTES:
            if external_system_attribute["REQUIRED"] and\
               external_system_attribute["NAME"] not in\
               external_system:
                fail = True
                break

        if fail:
            return False

        return True

    def check_capability(
            self, name: str,
            connection_name: str,
            capability: str) -> bool:
        if not GeneralsUtils.validate_string(name):
            raise TypeError(
                "The 'name' is not in the correct format")

        elif not GeneralsUtils.validate_string(connection_name):
            raise TypeError(
                "The 'connection_name' is not in the correct format")

        elif not GeneralsUtils.validate_string(capability):
            raise TypeError(
                "The 'capability' is not in the correct format")

        external_system_capabilities =\
            self.compose.get_capabilities(name, connection_name)

        external_system_capabilities_filtered = [
            external_system_capability
            for external_system_capability in external_system_capabilities
            if external_system_capability == capability]

        if len(external_system_capabilities_filtered) != 1:
            return False

        return True

    def compute_result(
            self,
            external_system_names,
            external_systems):
        result = []
        for external_system_name in external_system_names:
            result_get = None
            if len([external_system
                    for external_system in external_systems
                    if external_system[
                    Constants.EXTERNAL_SYSTEM_NAME_KEY] ==
                    external_system_name]) > 0:
                result_get = True

            else:
                result_get = False

            result.append({
                "externalSystemName": external_system_name,
                Constants.RESPONSE_BODY_RESULT_KEY: result_get})

        return result

    def enrich(self, external_system):
        external_system_language =\
            external_system[
                Constants.EXTERNAL_SYSTEM_LANGUAGE_KEY]

        if external_system_language == Constants.LANGUAGE_MULTI_SPEAK_ID:
            if Constants.EXTERNAL_SYSTEM_VERSION_KEY not in external_system:
                external_system[Constants.EXTERNAL_SYSTEM_VERSION_KEY] =\
                    ConfigurationManager.get_config(
                        "LANGUAGE_MULTI_SPEAK_DEFAULT_VERSION")

    def get(self, name: str) -> dict:
        if not GeneralsUtils.validate_string(name):
            raise TypeError(
                "The 'external_system_name' is not in the correct format")

        external_systems = self.compose.get_all()

        external_systems_filtered = [
            external_system
            for external_system in external_systems
            if external_system["name"] == name]

        if len(external_systems_filtered) != 1:
            raise SystemError(
                f"The '{name}' " +
                "external system was not found")

        return external_systems_filtered[0]

    def get_connection_by_connection_name(
            self,
            external_system_name: str,
            connection_name: str) -> dict:
        connections =\
            self.get_connections_by_external_system_name(external_system_name)

        if not GeneralsUtils.validate_string(connection_name):
            raise TypeError(
                "The 'connection_name' is not in the correct format")

        connections_filtered = [
            connection
            for connection in connections
            if connection["connectionName"] == connection_name]

        if len(connections_filtered) != 1:
            raise SystemError(
                f"The '{connection_name}' " +
                "connection was not found")

        return connections_filtered[0]

    def get_connections_by_external_system_name(
            self,
            external_system_name: str) -> list:
        result = []

        external_system = self.get(external_system_name)

        if "connection" not in\
           external_system:
            raise KeyError(
                "The key corresponding to the connections in " +
                "the external system '{name}' was not found")

        external_system_connections =\
            external_system["connection"]

        if not isinstance(external_system_connections, list) or\
           len(external_system_connections) == 0:
            raise SystemError(
                "No connections found in the " +
                f"external system '{external_system_name}'")

        external_system_name_key =\
            Constants.EXTERNAL_SYSTEM_NAME_KEY
        external_system_connection_name_key =\
            Constants.EXTERNAL_SYSTEM_CONNECTION_NAME_KEY

        for external_system_connection in external_system_connections:
            result_item = {
                external_system_name_key: external_system_name}

            if not isinstance(external_system_connection, dict) or\
               "name" not in external_system_connection:
                continue

            result_item[external_system_connection_name_key] =\
                external_system_connection["name"]

            if "configuration" not in external_system_connection or\
               not isinstance(
                    external_system_connection["configuration"], list):
                continue

            result_item.update(
                self.translate_external_system_connection_configurations(
                    external_system_connection["configuration"]))

            result.append(result_item)

        return result

    def get_connections_by_external_system_names(
            self,
            names: list) -> list:
        result = []

        if not isinstance(names, list):
            raise TypeError(
                "The 'external_system_names' is not in the correct format")

        elif len(names) == 0:
            raise ValueError(
                "The 'external_system_names' contains no data")

        for name in names:
            if not isinstance(name, str):
                continue

            try:
                result.extend(
                    self.get_connections_by_external_system_name(name))

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while getting the " +
                            "connection from an external system",
                    error=error,
                    process="Service")

        return result

    def get_names(self, data):
        external_system_names_key = "externalSystemNames"

        if not GeneralsUtils.check_dictionary_property(
           external_system_names_key,
           data):
            raise KeyError(
                    "Data does not contain node " +
                    f"'{external_system_names_key}'")

        return data[external_system_names_key]

    def obtain_propers(self, external_system_names: list) -> list:
        result =\
            self.get_connections_by_external_system_names(
                external_system_names)

        for external_system in result:
            if not self.check_attributes_external_system(external_system):
                result.remove(external_system)
                continue

            self.enrich(external_system)

        return result

    def process_common_method(self, method_name, data):
        result = []

        external_systems_names = self.get_names(data)

        external_systems = self.obtain_propers(external_systems_names)

        external_systems_clone = list(external_systems)
        for external_system in external_systems_clone:
            try:
                external_system_name = external_system[
                       Constants.EXTERNAL_SYSTEM_NAME_KEY]
                connection_name = external_system[
                       Constants.EXTERNAL_SYSTEM_CONNECTION_NAME_KEY]
                if not self.check_capability(
                   name=external_system_name,
                   connection_name=connection_name,
                   capability=method_name):
                    external_systems.remove(external_system)
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
                external_systems.remove(external_system)
                continue

            try:
                self.compose.send_message_command(
                    method_name,
                    external_system)

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to " +
                            "send message to execute the command",
                    error=error,
                    process="Service")
                external_systems.remove(external_system)

        result = self.compute_result(
            external_systems_names, external_systems)

        return result

    def translate_external_system_connection_configurations(
            self,
            configurations: list):
        result = {}
        for configuration in configurations:
            id_key = str(configuration["idKey"])
            key = None
            value = None

            if id_key not in self.__DICTIONARY__["configuration"]:
                continue

            key = self.__DICTIONARY__["configuration"][id_key]

            if key == Constants.EXTERNAL_SYSTEM_LANGUAGE_KEY:
                value = self.translate_external_system_language(
                    configuration["value"])

                if value is None:
                    continue

                result.update(value)

            else:
                value = configuration["value"]

                if key is None or value is None:
                    continue

                result[key] = value

        return result

    def translate_external_system_language(
            self,
            id_language: str):
        id_language = str(id_language)
        if id_language not in self.__DICTIONARY__["language"]:
            return None

        return self.__DICTIONARY__["language"][id_language]

    # -------------------------------------------------------------------

    def check_state(self, data: dict) -> list:
        result = []
        method_name = "EXTERNAL_SYSTEM_CHECK_STATE"

        external_systems_names = self.get_names(data)

        external_systems = self.obtain_propers(external_systems_names)

        external_systems_clone = list(external_systems)
        for external_system in external_systems_clone:
            try:
                self.compose.send_message_command(
                    method_name,
                    external_system)

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to send " +
                            "message to execute the command",
                    error=error,
                    process="Service")
                external_systems.remove(external_system)

        result = self.compute_result(
            external_systems_names, external_systems)

        return result

    def get_capabilities(self, data: dict) -> list:
        result = []
        method_name_get_capabilities =\
            "EXTERNAL_SYSTEM_GET_CAPABILITIES"
        method_name_get_subscription_capabilities =\
            "EXTERNAL_SYSTEM_GET_SUBSCRIPTION_CAPABILITIES"

        external_systems_names = self.get_names(data)

        external_systems = self.obtain_propers(external_systems_names)

        for external_system in list(external_systems):
            try:
                self.compose.send_message_command(
                    method_name_get_capabilities,
                    external_system)

                if external_system[Constants.EXTERNAL_SYSTEM_LANGUAGE_KEY] ==\
                   Constants.LANGUAGE_MULTI_SPEAK_ID:
                    self.compose.send_message_command(
                        method_name_get_subscription_capabilities,
                        external_system)

            except Exception as error:
                self.compose.system_log.add(
                    message="An error occurred while trying to send " +
                            "message to execute the command",
                    error=error,
                    process="Service")
                external_systems.remove(external_system)

        result = self.compute_result(
            external_systems_names, external_systems)

        return result

    def get_identifier(self, data: dict) -> list:
        method_name = "EXTERNAL_SYSTEM_GET_IDENTIFIER"

        return self.process_common_method(method_name, data)
