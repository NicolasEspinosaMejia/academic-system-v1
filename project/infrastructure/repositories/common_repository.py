from project.infrastructure.contexts.postgre_sql_context\
     import PostgreSqlContext
from project.infrastructure.repositories.repository_by_entities_definitions import \
     RepositoryByEntitiesDefinitions


class CommonRepository(RepositoryByEntitiesDefinitions):

    def __init__(self, connection_string_name="POSTGRESQL_DB_SET_AS",
                 entity_name=None):
        self.__context = PostgreSqlContext(connection_string_name)

        RepositoryByEntitiesDefinitions.__init__(self, self.__context,
                                                 entity_name)
