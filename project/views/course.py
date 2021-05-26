from project.composers.course_compose import CourseCompose
from project.services.course_service import CourseService
from project.configuration_manager import ConfigurationManager
from project.infrastructure.repositories.common_repository import CommonRepository
from project.resources.decorators.view_aspect import ViewAspect
from project.infrastructure.repositories.repository_by_entities_definitions\
    import RepositoryByEntitiesDefinitions


@ViewAspect
def manage_course(data):
    service = get_service()
    result = service.manage_course(data)

    return result

@ViewAspect
def manage_course_delete(data):
    service = get_service()
    result = service.manage_course_delete(data)

    return result

@ViewAspect
def get_course():
    service = get_service()
    result = service.get_course()

    return result

def get_service():
    """This method is in charge of making the instances of the services
       and the compose that will be used generically

    Returns:
        object:This method returns an instance of the parent service that
               is being used
    """
    bridge_command_repository = CommonRepository()
    microservice = ConfigurationManager.microservice
    sender_queue_service_client = microservice.sender_queue_service_client
    compose = CourseCompose(
        database_cache_repository=bridge_command_repository,
        sender_queue_service_client=sender_queue_service_client)
    service = CourseService(compose=compose,
                            repository=RepositoryByEntitiesDefinitions)

    return service
