from project.composers.compose import Compose

class CourseCompose(Compose):

    def __init__(self, database_cache_repository, sender_queue_service_client):
        self.repository = database_cache_repository

    def get_course(self):
        return self.repository.select_all(entity_name="course")

    def manage_course_add(self, data_structure):
        return self.repository.insert(values=data_structure,
                                      entity_name="course")

    def manage_course_del(self, data_structure):
        return self.repository.delete(id=data_structure["identifier"],
                                      entity_name="course")

    def manage_course_upd(self, data_structure):
        identifier = data_structure["identifier"]
        del data_structure["identifier"]
        return self.repository.update(id=identifier,
                                      values=data_structure,
                                      entity_name="course")
