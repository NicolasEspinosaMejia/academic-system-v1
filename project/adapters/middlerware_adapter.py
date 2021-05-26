import abc


class MiddlerwareAdapter(abc.ABC):

    @abc.abstractmethod
    def get_queue_service_client(self):
        raise NotImplementedError
