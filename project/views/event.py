from project.composers.event_compose import EventCompose
from project.configuration_manager import ConfigurationManager
from project.resources.decorators.view_aspect import ViewAspect
from project.services.event_service import EventService


@ViewAspect
def subscribe(data):
    """The requester asks the receiver to start monitoring the events
    of a set of meters

    Args:
        data (dict): Ajustar

    Returns:
        dict: Ajustar
    """
    service = get_service()
    result = service.subscribe(data)

    return result


@ViewAspect
def get_on_demand(data):
    """The requester asks the receiver to start monitoring the events
    of a set of meters

    Args:
        data (dict): The data have externalSystemName, connectionName,
                     array of devices and eventTypeCodes

    Returns:
        dict: the result with the success and the fail data
    """
    service = get_service()
    result = service.get_on_demand(data)

    return result


def get_service():
    microservice = ConfigurationManager.microservice
    database_cache_repository = microservice.database_cache_repository
    sender_queue_service_client = microservice.sender_queue_service_client
    compose = EventCompose(
        database_cache_repository=database_cache_repository,
        sender_queue_service_client=sender_queue_service_client)
    service = EventService(
        compose=compose)

    return service
