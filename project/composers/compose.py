import json

from project.constants import Constants
from project.configuration_manager import ConfigurationManager
from project.logs.system_log import SystemLog
from project.models.queue_message_model import QueueMessageModel
from project.resources.utils.generals_utils import GeneralsUtils
from project.resources.utils.queue_service_utils import QueueServiceUtils


class Compose:

    local_storage = {}
    owner = ""
    transaction_id = ""
    user_id = ""

    def __init__(
            self,
            database_cache_repository=None,
            sender_queue_service_client=None):
        self.database_cache_repository = database_cache_repository
        self.sender_queue_service_client = sender_queue_service_client
        self.system_log = SystemLog
        self.local_storage = {}
        self.set_global_parameters()

    def get_database_cache_value(self, key):
        if key not in self.local_storage:
            self.local_storage[key] =\
                json.loads(self.database_cache_repository.get(key))

        return self.local_storage[key]

    def send_message_command(
            self,
            method_name: str,
            external_system: dict,
            data: dict = None) -> bool:
        external_system_key = Constants.EXTERNAL_SYSTEM_KEY

        data = data or {}

        if not GeneralsUtils.validate_string(method_name) or\
           not isinstance(external_system, dict) or\
           not isinstance(data, dict):
            raise ValueError("Parameters are not correct")

        external_system_language =\
            external_system[Constants.EXTERNAL_SYSTEM_LANGUAGE_KEY]
        external_system_version =\
            external_system[Constants.EXTERNAL_SYSTEM_VERSION_KEY]

        queue_message_event_type =\
            QueueServiceUtils.get_message_event_type_by_method_name(
                    external_system_language,
                    external_system_version,
                    method_name)

        data[external_system_key] = external_system

        self.sender_queue_service_client.send_message(
            ConfigurationManager.get_config("QUEUE_COMMAND_NAME"),
            QueueMessageModel(
                "fun-commandExecutor",
                queue_message_event_type,
                [data]))

    def set_global_parameters(self):
        global_data_user_id_key =\
            Constants.GLOBAL_DATA_USER_ID_KEY
        global_data_transaction_id_key =\
            Constants.GLOBAL_DATA_TRANSACTION_ID_KEY
        global_data_owner_data_key =\
            Constants.GLOBAL_DATA_OWNER_KEY

        self.user_id =\
            GeneralsUtils.get_global_data(global_data_user_id_key)
        self.transaction_id =\
            GeneralsUtils.get_global_data(global_data_transaction_id_key)
        self.owner =\
            GeneralsUtils.get_global_data(global_data_owner_data_key)
