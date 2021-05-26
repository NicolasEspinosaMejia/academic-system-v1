from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from project.configuration_manager import ConfigurationManager
from project.constants import Constants
from project.resources.utils.rule_validation import ValidationError
from project.resources.utils.generals_utils import GeneralsUtils


class PostgreSqlContext:
    auto_dispose_bind = None
    SESSION_QUERY = "SET SESSION {} = {}"
    __session_maker = None
    __session = None
    engine = None

    def __init__(self, connection_string_name, auto_dispose_bind=True):
        self.auto_dispose_bind = auto_dispose_bind
        self.configure(connection_string_name)

    def get_connection_string_configuration(self, key):
        return self.__configurations.get(key)

    def configure(self, connection_string_name):
        connection_string_parts = ConfigurationManager.\
            get_connection_string(connection_string_name).split(',')

        if len(connection_string_parts) not in {3, 4}:
            raise Exception('Wrong number of connection parameters.')

        database_system, driver, parameters = connection_string_parts[:3]
        configurations = ''

        if len(connection_string_parts) == 4 and\
           GeneralsUtils.validate_string(connection_string_parts[3]):
            configurations = "?{}".format(connection_string_parts[3])

        if database_system not in Constants.DATABASE_SYSTEMS:
            raise Exception('Not supported database backend.')

        if driver and driver not in Constants.DATABASE_DRIVERS:
            raise Exception('Not supported database driver.')

        connection_string_split = "{}{}://{}{}".\
            format(database_system,
                   f'+{driver}' if driver else '',
                   parameters,
                   configurations).split("?")

        self.__connection_string = connection_string_split.pop(0)
        self.__configurations = {}
        self.__connect_args = {}

        try:
            if connection_string_split:
                configurations_array = connection_string_split[0].split("&")
                for configuration in configurations_array:
                    key, value = configuration.split("=")
                    self.__configurations[key] = value

                if database_system == "redshift":
                    self.__connect_args = self.__configurations.copy()
                    self.__connect_args.pop("schema", "")
        except Exception as error:
            raise Exception("", error)

        self.engine = create_engine(
            self.__connection_string,
            echo=False,
            connect_args=self.__connect_args
        )
        self.__session_maker = sessionmaker(bind=self.engine)

    def get_connection_string(self):
        return self.__connection_string

    @contextmanager
    def session(self):
        self.__session = self.__session_maker()
        try:
            if self.__session.bind.name in Constants.DATABASE_WITH_AUDIT:
                self.__set_variables_session(self.__session)
            yield self.__session
            self.__session.commit()
        except ValidationError:
            raise
        except Exception as error:
            self.__session.rollback()
            raise Exception(
                    "Error requesting to make a transaction to the database",
                    error
                  )

        finally:
            self.__session.close()
            if self.auto_dispose_bind:
                self.dispose()

    def dispose(self):
        if self.__session:
            self.__session.bind.dispose()

    def __set_variables_session(self, session):
        """This method assigns session variables for the audit.

        Args:
            session: session object

        Returns:
            None
        """
        variables = {
            "ip": [
                Constants.GLOBAL_SESSION_SOURCE_IP_KEY,
                GeneralsUtils.get_global_data(Constants.GLOBAL_DATA_IP_KEY)
            ],
            "owner_id": [
                Constants.GLOBAL_SESSION_OWNER_ID_KEY,
                GeneralsUtils.get_global_data(Constants.GLOBAL_DATA_OWNER_KEY)
            ],
            "source_id": [
                Constants.GLOBAL_SESSION_SOURCE_ID_KEY,
                Constants.NAME_SERVICE
            ],
            "transaction_id": [
                Constants.GLOBAL_SESSION_TRANSACTION_ID_KEY,
                GeneralsUtils.get_global_data(
                    Constants.GLOBAL_DATA_TRANSACTION_ID_KEY)
            ],
            "user_id": [
                Constants.GLOBAL_SESSION_USER_ID_KEY,
                GeneralsUtils.get_global_data(
                    Constants.GLOBAL_DATA_USER_ID_KEY)
            ],
        }

        for key, value in variables.items():
            if value[1]:
                session.execute(self.SESSION_QUERY.format(value[0],
                                                          "'"+value[1]+"'"))
