import os

from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils


class ConfigurationManager():

    connection_strings = {}
    database_cache_keys = {}

    microservice = None

    @staticmethod
    def __get_config_by_group__(local_storage, config_group_name, config_name):
        if config_name in os.environ:
            return os.environ[config_name]

        if len(local_storage) == 0:
            local_storage = ConfigurationManager.\
                get_config(config_group_name)

        if config_name not in local_storage:
            raise KeyError(
                "The requested configuration group string was not found")

        return local_storage[config_name]

    @staticmethod
    def get_api_version() -> str:
        try:
            result = ConfigurationManager.get_config(
                Constants.CONFIG_APP_VERSION_KEY)

        except Exception:
            result = "Unknown"

        return result

    @staticmethod
    def get_connection_string(connection_string_name: str) -> str:
        return ConfigurationManager.__get_config_by_group__(
            ConfigurationManager.connection_strings,
            Constants.CONFIG_CONNECTION_STRINGS_KEY,
            connection_string_name)

    @staticmethod
    def get_config(key, group=None):
        if key in os.environ:
            return os.environ[key]

        configurations = GeneralsUtils.read_file("config.yml", "yaml")

        configs = configurations["pyms"]["config"]
        if group:
            if group in configs:
                configs = configs[group]

            else:
                raise KeyError(
                        f"The requested configuration group '{group}' " +
                        "does not exist")

        if key not in configs:
            raise KeyError("The requested configuration '{key}' " +
                           "does not exist")

        return configs[key]

    @staticmethod
    def get_database_cache_key(database_cache_key: str) -> str:
        return ConfigurationManager.__get_config_by_group__(
            ConfigurationManager.database_cache_keys,
            Constants.CONFIG_DATABASE_CACHE_KEYS_KEY,
            database_cache_key)
