from project.composers.metering_system_compose import MeteringSystemCompose
from project.configuration_manager import ConfigurationManager
from project.resources.decorators.view_aspect import ViewAspect
from project.services.metering_system_service import MeteringSystemService


@ViewAspect
def discover(data):
    service = get_service()
    result = service.discover(data)

    return result


def get_service():
    microservice = ConfigurationManager.microservice
    database_cache_repository = microservice.database_cache_repository
    sender_queue_service_client = microservice.sender_queue_service_client
    compose = MeteringSystemCompose(
        database_cache_repository=database_cache_repository,
        sender_queue_service_client=sender_queue_service_client)
    service = MeteringSystemService(
        compose=compose)

    return service
