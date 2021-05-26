from project.composers.external_system_compose import ExternalSystemCompose
from project.configuration_manager import ConfigurationManager
from project.resources.decorators.view_aspect import ViewAspect
from project.services.external_system_service import ExternalSystemService


@ViewAspect
def check_state(data):
    service = get_service()
    result = service.check_state(data)

    return result


@ViewAspect
def get_capabilities(data):
    service = get_service()
    result = service.get_capabilities(data)

    return result


@ViewAspect
def get_identifier(data):
    service = get_service()
    result = service.get_identifier(data)

    return result


def get_service():
    microservice = ConfigurationManager.microservice
    database_cache_repository = microservice.database_cache_repository
    sender_queue_service_client = microservice.sender_queue_service_client
    compose = ExternalSystemCompose(
        database_cache_repository=database_cache_repository,
        sender_queue_service_client=sender_queue_service_client)
    service = ExternalSystemService(
        compose=compose)

    return service
