

import json

from project.adapters.database_cache_repository_adapter import\
    DatabaseCacheRepositoryAdapter
from project.resources.utils.generals_utils import GeneralsUtils


class RedisRepository(DatabaseCacheRepositoryAdapter):

    def __init__(self, context):
        self.__context = context

    def get(self, key):
        if not GeneralsUtils.validate_string(key):
            raise TypeError("The 'key' is not in the correct format")

        return self.__context.client.get(key)

    def set(self, key, value):
        if not GeneralsUtils.validate_string(key):
            raise TypeError("The 'key' is not in the correct format")

        if isinstance(value, (dict, list)):
            value = json.dumps(value)

        self.__context.client.set(key, value)
