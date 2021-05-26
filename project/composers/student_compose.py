from project.composers.compose import Compose

class StudentCompose(Compose):

    def __init__(self, database_cache_repository, sender_queue_service_client):
        self.repository = database_cache_repository

    def associate_student_course(self, data_structure):
        return self.repository.insert(values=data_structure,
                                      entity_name="studentCourse")

    def associate_student_address(self, data_structure):
        return self.repository.insert(values=data_structure,
                                      entity_name="studentAddress")

    def disassociate_student_course(self, data_structure):
        return self.repository.delete(id=data_structure["identifier"],
                                      entity_name="studentCourse")

    def disassociate_student_address(self, data_structure):
        return self.repository.delete(id=data_structure["identifier"],
                                      entity_name="studentAddress")

    def get_student(self):
        return self.repository.select_all(entity_name="student")

    def manage_student_add(self, data_structure):
        return self.repository.insert(values=data_structure,
                                      entity_name="student")

    def manage_student_del(self, data_structure):
        return self.repository.delete(id=data_structure["identifier"],
                                      entity_name="student")

    def manage_student_upd(self, data_structure):
        identifier = data_structure["identifier"]
        del data_structure["identifier"]
        return self.repository.update(id=identifier,
                                      values=data_structure,
                                      entity_name="student")
