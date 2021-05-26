import abc


class HandlerQueueServiceClientAdapter(abc.ABC):

    @abc.abstractmethod
    def receive_message(self, message):
        raise NotImplementedError


class SenderQueueServiceClientAdapter(abc.ABC):

    @abc.abstractmethod
    def send_message(self, message):
        raise NotImplementedError
