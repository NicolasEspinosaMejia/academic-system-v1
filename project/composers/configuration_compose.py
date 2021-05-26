from project.composers.compose import Compose


class ConfigurationCompose(Compose):

    def __init__(
            self,
            database_cache_repository=None,
            sender_queue_service_client=None):
        Compose.__init__(
            self,
            database_cache_repository,
            sender_queue_service_client)
