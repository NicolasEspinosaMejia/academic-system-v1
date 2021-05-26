import redis

from project.configuration_manager import ConfigurationManager
from project.resources.utils.generals_utils import GeneralsUtils


class RedisContext():

    def __init__(self, connection_string_name: str, db: int = 0):
        kwargs = {}

        if not GeneralsUtils.validate_string(connection_string_name):
            raise TypeError(
                "The 'connection_string_name' is not in the correct format")

        elif not isinstance(db, int):
            raise TypeError(
                "The 'db' is not in the correct format")

        try:
            connection_string = ConfigurationManager.\
                get_connection_string(connection_string_name)

            for connection_parameter in connection_string.split(","):
                connection_parameter_key, connection_parameter_value =\
                    connection_parameter.split("=")
                kwargs[connection_parameter_key] = connection_parameter_value

            kwargs["db"] = db

        except Exception as error:
            raise ValueError("Error configuring connection string", error)

        self.client = redis.Redis(**kwargs)
