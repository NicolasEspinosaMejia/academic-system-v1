from project.configuration_manager import ConfigurationManager
from project.composers.compose import Compose
from project.resources.utils.generals_utils import GeneralsUtils


class ExternalSystemCompose(Compose):

    def get_all(self) -> dict:
        result = {}

        database_cache_external_systems_key =\
            ConfigurationManager.get_database_cache_key(
                 "EXTERNAL_SYSTEMS")

        result = self.get_database_cache_value(
            database_cache_external_systems_key)

        if result is None or len(result) == 0:
            raise ValueError("No external system data found " +
                             "in the cache database")

        return result

    def get_capabilities(self, name: str, connection_name: str) -> list:
        result = {}

        if not GeneralsUtils.validate_string(name):
            raise TypeError(
                "The 'name' is not in the correct format")

        elif not GeneralsUtils.validate_string(connection_name):
            raise TypeError(
                "The 'connection_name' is not in the correct format")

        database_cache_external_system_capabilities_key =\
            ConfigurationManager.get_database_cache_key(
                "EXTERNAL_SYSTEM_CAPABILITIES").format(name, connection_name)

        result = self.get_database_cache_value(
            database_cache_external_system_capabilities_key)

        if result is None or len(result) == 0:
            raise ValueError("No external system capabilities for " +
                             f"{name}-{connection_name} data found in " +
                             "the cache database")

        return result
