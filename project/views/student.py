from project.composers.student_compose import StudentCompose
from project.services.student_service import StudentService
from project.infrastructure.repositories.common_repository import CommonRepository
from project.configuration_manager import ConfigurationManager
from project.infrastructure.repositories.repository_by_entities_definitions\
    import RepositoryByEntitiesDefinitions
from project.resources.decorators.view_aspect import ViewAspect


@ViewAspect
def manage_student(data):
    service = get_service()
    result = service.manage_student(data)

    return result

@ViewAspect
def manage_student_delete(data):
    service = get_service()
    result = service.manage_student_delete(data)

    return result

@ViewAspect
def associate_student_course(data):
    service = get_service()
    result = service.associate_student_course(data)

    return result

@ViewAspect
def associate_student_address(data):
    service = get_service()
    result = service.associate_student_address(data)

    return result

@ViewAspect
def disassociate_student_course(data):
    service = get_service()
    result = service.disassociate_student_course(data)

    return result

@ViewAspect
def disassociate_student_address(data):
    service = get_service()
    result = service.disassociate_student_address(data)

    return result

@ViewAspect
def get_student():
    service = get_service()
    result = service.get_student()

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
    compose = StudentCompose(
        database_cache_repository=bridge_command_repository,
        sender_queue_service_client=sender_queue_service_client)
    service = StudentService(compose=compose,
                             repository=RepositoryByEntitiesDefinitions)

    return service
