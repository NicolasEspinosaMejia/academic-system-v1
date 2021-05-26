from project.composers.schedule_compose import ScheduleCompose
from project.configuration_manager import ConfigurationManager
from project.resources.decorators.view_aspect import ViewAspect
from project.services.schedule_service import ScheduleService


@ViewAspect
def create_reading_schedule(data):
    """this method is used for comunicate of swagger with
    service

    Args:
        data (dict): data request of swagger with list of readings
        that have externalSystemName, connectionName, deviceIds,
        readingTypeCodes and schedule

    Returns:
        dict: ata processed and sent to sqs
    """
    service = get_service()
    result = service.create_reading_schedule(data)

    return result


@ViewAspect
def enable_reading_schedule(data):
    """Ajustar

    Args:
        data (dict): Ajustar

    Returns:
        result (list): Ajustar
    """
    service = get_service()
    result = service.enable_reading_schedule(data)

    return result


def get_service():
    microservice = ConfigurationManager.microservice
    database_cache_repository = microservice.database_cache_repository
    sender_queue_service_client = microservice.sender_queue_service_client
    compose = ScheduleCompose(
        database_cache_repository=database_cache_repository,
        sender_queue_service_client=sender_queue_service_client)
    service = ScheduleService(
        compose=compose)

    return service
