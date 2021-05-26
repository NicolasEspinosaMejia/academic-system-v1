from project.composers.configuration_compose import ConfigurationCompose
from project.configuration_manager import ConfigurationManager
from project.resources.decorators.view_aspect import ViewAspect
from project.services.configuration_service import ConfigurationService


@ViewAspect
def check_state(component: str = None):
    service = get_service()
    result = service.check_state(component)

    return result


def get_service():
    microservice = ConfigurationManager.microservice
    database_cache_repository = microservice.database_cache_repository
    sender_queue_service_client = microservice.sender_queue_service_client
    compose = ConfigurationCompose(
        database_cache_repository=database_cache_repository,
        sender_queue_service_client=sender_queue_service_client)
    service = ConfigurationService(
        compose=compose)

    return service
