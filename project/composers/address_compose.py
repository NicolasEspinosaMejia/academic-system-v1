from project.composers.compose import Compose

class AddressCompose(Compose):

    def __init__(self, database_cache_repository, sender_queue_service_client):
        self.repository = database_cache_repository

    def get_address(self):
        return self.repository.select_all(entity_name="address")

    def manage_address_add(self, data_structure):
        return self.repository.insert(values=data_structure,
                                      entity_name="address")

    def manage_address_del(self, data_structure):
        return self.repository.delete(id=data_structure["identifier"],
                                      entity_name="address")

    def manage_address_upd(self, data_structure):
        identifier = data_structure["identifier"]
        del data_structure["identifier"]
        return self.repository.update(id=identifier,
                                      values=data_structure,
                                      entity_name="address")