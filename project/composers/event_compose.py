from project.composers.compose import Compose
from project.configuration_manager import ConfigurationManager
from project.resources.utils.generals_utils import GeneralsUtils


class EventCompose(Compose):

    def get_configuration(self, transaction_id: str) -> str:
        """This methos is used for extracted the configuration of
           transactionId

        Args:
            transaction_id (str): the variable that search in redis

        Returns:
            str: configuration
        """
        result = {}

        if not GeneralsUtils.validate_string(transaction_id):
            raise TypeError(
                "The 'variable_id' is not in the correct format")

        database_cache_reading_type_code_key =\
            ConfigurationManager.get_database_cache_key(
                "TRANSACTIONS").format(transaction_id)

        result = self.get_database_cache_value(
            database_cache_reading_type_code_key)

        if result is None or len(result) == 0:
            raise ValueError(
                f"No transactions {transaction_id}" +
                " data found in the cache database")

        return result

    def get_event_type_codes(self) -> list:
        """This methos is used for extracted the eventTypesCodes

        Returns:
            list: eventTypesCodes
        """
        result = self.get_database_cache_value(
            "eventTypeCodes")

        if result is None or len(result) == 0:
            raise ValueError(
                f"No list of EVENT_TYPE_CODE " +
                "in the cache database")

        return result
