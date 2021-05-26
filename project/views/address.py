from project.composers.address_compose import AddressCompose
from project.services.address_service import AddressService
from project.configuration_manager import ConfigurationManager
from project.resources.decorators.view_aspect import ViewAspect


@ViewAspect
def manage_address(data):
    service = get_service()
    result = service.manage_address(data)

    return result

@ViewAspect
def get_address(data):
    service = get_service()
    result = service.get_address(data)

    return result

def get_service():
    """This method is in charge of making the instances of the services
       and the compose that will be used generically

    Returns:
        object:This method returns an instance of the parent service that
               is being used
    """
    microservice = ConfigurationManager.microservice
    database_cache_repository = microservice.database_cache_repository
    sender_queue_service_client = microservice.sender_queue_service_client
    compose = AddressCompose(
        database_cache_repository=database_cache_repository,
        sender_queue_service_client=sender_queue_service_client)
    service = AddressService(
        compose=compose)

    return service
