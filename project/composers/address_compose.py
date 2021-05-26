from project.composers.compose import Compose

class AddressCompose(Compose):

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

    def manage_address(self, data_structure):
        print(data_structure)

    def get_address(self, data):
        print(data)
