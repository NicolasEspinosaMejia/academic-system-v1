from flask_cors import CORS
from pyms.flask.app import Microservice

from project.configuration_manager import ConfigurationManager
from project.handler_sqs_client_thread_initializer import\
    HandlerSqsClientThreadInitializer
from project.implementations.sqs_client import\
    HandlerSqsClientWithAwsSession,\
    SenderSqsClientWithAwsSession
from project.infrastructure.contexts.aws_context import\
    AwsContextWithSession
from project.infrastructure.contexts.redis_context import RedisContext
from project.processors.configuration import\
    Configuration
from project.processors.control_action import\
    ControlAction
from project.infrastructure.repositories.redis_repository import\
    RedisRepository


class AcademicSystemMicroservice(Microservice):

    def init_libs(self):
        self.config["CORS_HEADERS"] = "Content-Type"
        self.init_local_services()

    def init_local_services(self) -> None:
        self.middlerware_context = AwsContextWithSession()
        database_cache_connection_string_name = "REDIS_EC_CROSS"
        self.database_cache_context = RedisContext(
            database_cache_connection_string_name)
        self.database_cache_repository =\
            RedisRepository(self.database_cache_context)

        self.handler_queue_service_client =\
            HandlerSqsClientWithAwsSession(
                middlerware_adapter=self.middlerware_context,
                processors={
                    "configuration": Configuration(),
                    "controlAction": ControlAction()
                })
        HandlerSqsClientThreadInitializer(self.handler_queue_service_client)

        self.sender_queue_service_client =\
            SenderSqsClientWithAwsSession(self.middlerware_context)


def create_app():
    microservice = AcademicSystemMicroservice(path=__file__)
    ConfigurationManager.microservice = microservice

    app = microservice.create_app()
    CORS(app, resources={r"/academic-system/*": {"origins": "*"}})

    return app
