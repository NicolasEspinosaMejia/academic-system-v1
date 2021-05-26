from project.composers.reading_compose import ReadingCompose
from project.configuration_manager import ConfigurationManager
from project.resources.decorators.view_aspect import ViewAspect
from project.services.reading_service import ReadingService


@ViewAspect
def get_on_demand(data):
    """this method is used for comunicate of swagger with
    service

    Args:
        data (dict): data request of swagger with list of readings
        that have externalSystemName, connectionName, deviceIds,
        and readingTypeCodes

    Returns:
        dict: data processed and sent to sqs
    """

    service = get_service()
    result = service.get_on_demand(data)

    return result


def get_service():
    microservice = ConfigurationManager.microservice
    database_cache_repository = microservice.database_cache_repository
    sender_queue_service_client = microservice.sender_queue_service_client
    compose = ReadingCompose(
        database_cache_repository=database_cache_repository,
        sender_queue_service_client=sender_queue_service_client)
    service = ReadingService(
        compose=compose)

    return service
