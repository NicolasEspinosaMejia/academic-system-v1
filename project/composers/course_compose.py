from project.composers.compose import Compose

class CourseCompose(Compose):

    def __init__(
            self,
            entities_parameters,
            repository,
            message_broker_adapter=None):
        Compose.__init__(
            self,
            entities_parameters=entities_parameters,
            repository=repository,
            message_broker_adapter=message_broker_adapter)

    def manage_course(self, data_structure):
        print(data_structure)

    def get_course(self, data):
        print(data)
