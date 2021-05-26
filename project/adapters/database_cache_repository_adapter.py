import abc


class DatabaseCacheRepositoryAdapter(abc.ABC):

    @abc.abstractmethod
    def get(self, key):
        raise NotImplementedError

    @abc.abstractmethod
    def set(self, key, data):
        raise NotImplementedError
