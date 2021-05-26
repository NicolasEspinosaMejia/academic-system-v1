from project.composers.control_action_compose import ControlActionCompose
from project.configuration_manager import ConfigurationManager
from project.resources.decorators.view_aspect import ViewAspect
from project.services.control_action_service import ControlActionService


@ViewAspect
def execute(data):
    """This method is in charge of executing the control actions,
        as the case may be.

    Args:
        data (dict): This component is a dictionary that is made
                        up of control actions

    Returns:
        list: This method returns a list of already validated
        control actions, which will be identified with a true
        or false according to the validation case they have had.
    """
    service = get_service()
    result = service.execute(data)

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
    compose = ControlActionCompose(
        database_cache_repository=database_cache_repository,
        sender_queue_service_client=sender_queue_service_client)
    service = ControlActionService(
        compose=compose)

    return service
