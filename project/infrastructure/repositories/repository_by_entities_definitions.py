from sqlalchemy import MetaData, or_, func, select
from project.resources.utils.entity_utils import EntityUtils
from project.resources.utils.generals_utils import GeneralsUtils
from project.resources.utils.sqlalchemy_utils import SqlalchemyUtils


class RepositoryByEntitiesDefinitions:
    def __init__(self, context, entity_name=None):
        self.__context = context
        self.__entity_name = entity_name
        self.meta_data = MetaData(context.session(),
                                   schema=self.__context.
                                   get_connection_string_configuration(
                                       "schema"))

    def get_relation_validate(self, device_id, service_point_id):
        utils_sqlalchemy = SqlalchemyUtils()
        session = self.__context.session()
        meta_data = MetaData(session,
                             schema=self.__context.
                             get_connection_string_configuration(
                                 "schema"))
        array_data =\
            utils_sqlalchemy.configure_table("validationRelationDevice",
                                             meta_data)
        statement =\
            array_data.select().where(
                or_(array_data.c.identifier == device_id,
                    array_data.c.identifier == service_point_id))
        with session as connection:
            query_result = connection.execute(statement)

        return query_result

    def query(self, operation, entity_name=None, options=None):
        context = self.__context
        have_id = False
        entity_name = entity_name or self.__entity_name

        if 'filters' in options and len(options['filters']) == 3 and \
                GeneralsUtils.validate_string(options['filters'][0]):
            options['filters'] = [options['filters']]

        if not isinstance(entity_name, str):
            raise Exception("The entity name has not been configured")

        if self.__context is None:
            raise Exception("The database context has not been configured")

        if not isinstance(options, dict):
            options = {}

        if "id" in options and options["id"] is not None:
            have_id = True

        session = context.session()

        if entity_name == "device_insert" or\
           entity_name == "task_varaibles_insert" or\
           entity_name == "task_services_points_insert":
            with session as connection:
                connection.add_all(options["values"])

            return True

        table_sqlalchemy = SqlalchemyUtils.configure_table(
            entity_name, self.meta_data)

        if operation in {'delete', 'select', 'update'} and have_id:
            primary_key_columns = getattr(table_sqlalchemy.primary_key,
                                          "columns")

            if len(primary_key_columns) != 1:
                raise Exception(
                    "Common delete, update or selection "
                    "operation requires a primary key definition")

            primary_key_column = next(iter(primary_key_columns))

        statement = table_sqlalchemy.select()
        if operation in ('select', 'count'):
            option_keys = 'distinct', 'group_by', 'filters', 'order_by', \
                          'paginate', 'udfs'
            if any(key in options for key in option_keys):
                statement = SqlalchemyUtils.generate_select_statement(
                    entity_name, table_sqlalchemy, options)

        elif operation == "update":
            values = options["values"]

            if not isinstance(values, dict):
                raise Exception('The values to update do not correspond to the'
                                ' expected format')

            statement = SqlalchemyUtils.generate_update_statement(
                entity_name, table_sqlalchemy, options, values)

        elif operation == "insert":
            values = options["values"]

            if isinstance(values, dict):
                values = [values]

            values_statement_keys = [EntityUtils.translate_dictionary(
                entity_name=entity_name,
                entity_properties=item) for item in values]

            primary_keys = list(table_sqlalchemy.primary_key.columns)
            statement = table_sqlalchemy.insert().values(
                values_statement_keys).returning(*primary_keys)

        elif operation == "delete":
            if have_id or "options" in options:
                statement = table_sqlalchemy.delete(None)
            else:
                raise Exception("When requesting a deletion it is mandatory "
                                "to specify the id of the record to delete")

        if 'options' in options and operation in ("update", "delete"):
            statement = SqlalchemyUtils.generate_where_statement(
                entity_name, options, statement, table_sqlalchemy)

        if have_id:
            statement = statement.where(primary_key_column == options["id"])

        if operation == 'count':
            select_from = statement.alias('subquery')
            statement = select([func.count()]).select_from(select_from)

        with session as connection:
            query_result = connection.execute(statement)

        return query_result

    def count(self, entity_name=None, options=None):
        result = self.query('count', entity_name or self.__entity_name, options)
        return result.fetchone()[0]

    def delete(self, id, entity_name=None):
        query_result = self.query(
            "delete",
            entity_name or self.__entity_name,
            {
                "id": id
            }
        )

        if query_result.rowcount != 1:
            raise Exception(
                "Fatal error: deletion operation has affected more than one column, {}".format(id))

        return True

    def insert(self, values, entity_name=None):
        result = self.query("insert", entity_name or self.__entity_name,
                            {"values": values})
        if result is True or not result.returns_rows:
            return True
        ids = [id[0] if len(id) < 2 else id for id in result.fetchall()]
        return ids if len(ids) > 1 else ids[0]

    def select(self, entity_name=None, options=None):
        # T
        result = []
        fail = False
        error_detected = None

        query_result = self.query(
            "select",
            entity_name or self.__entity_name,
            options
        )

        for row in query_result:
            try:
                result.append(
                    EntityUtils.translate_dictionary(
                        entity_name=entity_name or self.__entity_name,
                        table=dict(row))
                )

            except Exception as error:
                error_detected = error
                fail = True
                break

        if fail:
            raise Exception("", error_detected)

        return result

    def select_all(self, entity_name=None):
        # T
        result = []
        fail = False
        error_detected = None

        query_result = self.query(
            "select",
            entity_name=entity_name,
            options={}
        )

        for row in query_result:
            try:
                result.append(
                    EntityUtils.translate_dictionary(
                        entity_name=entity_name or self.__entity_name,
                        table=dict(row)))

            except Exception as error:
                fail = True
                error_detected = error
                break

        if fail:
            raise Exception("", error_detected)

        return result

    def select_distinct(self, column_name, entity_name=None):
        # T
        result = []
        fail = False
        error_detected = None

        if not isinstance(column_name, str):
            raise Exception("")

        query_result = self.query(
            "select",
            {"distinct": column_name})

        for row in query_result:
            try:
                result.append(
                    EntityUtils.translate_dictionary(
                        entity_name=entity_name or self.__entity_name,
                        table=dict(row)))

            except Exception as error:
                fail = True
                error_detected = error
                break

        if fail:
            raise Exception("", error_detected)

        return result

    def select_group_by(
            self,
            column_name,
            with_total_count=False,
            entity_name=None,
            options=None):
        result = []
        fail = False
        error_detected = None

        if not isinstance(column_name, str):
            raise Exception("")

        if not isinstance(with_total_count, bool):
            with_total_count = False

        options = options or {}
        options["group_by"] = {
            "column_name": column_name,
            "with_total_count": with_total_count
        }

        query_result = self.query(
            "select",
            entity_name or self.__entity_name,
            options
        )

        for row in query_result:
            try:
                result.append(row)

            except Exception as error:
                fail = True
                error_detected = error
                break

        if fail:
            raise Exception("", error_detected)

        return result

    def select_one(self, id, entity_name=None):
        # T
        result = []
        fail = False
        error_detected = None

        query_result = self.query(
            "select",
            entity_name,
            {
                "id": id
            })

        for row in query_result:
            try:
                result.append(
                    EntityUtils.translate_dictionary(
                        entity_name=entity_name or self.__entity_name,
                        table=dict(row)))

            except Exception as error:
                fail = True
                error_detected = error
                break

        if fail:
            raise Exception("", error_detected)

        return result

    def update(self, id, values, entity_name=None):
        query_result = self.query(
            "update",
            entity_name or self.__entity_name,
            {
                "id": id,
                "values": values
            }
        )

        if query_result.rowcount != 1:
            raise Exception

        return True

    def update_where(self, values, options, entity_name=None):
        self.query("update", entity_name or self.__entity_name,
                   dict(values=values, **options))

        return True

    def update_compound_key(self, ids, values, entity_name=None):
        """ This method is using for tables  update, when this have a compound primary key. """
        try:
            options = {"options": ids, "values": values}
            query_result = self.query(
                "update", entity_name or self.__entity_name, options)
        except Exception as error:
            error_detected = error

            if query_result.rowcount != 1:
                raise Exception(
                    "Fatal Error: The data was not updated.",
                    error_detected)

        return True

    def delete_compound_key(self, ids, entity_name=None):
        """ This method is using for tables  delete,
        when this have a compound primary key. """
        try:
            query_result = self.query(
                "delete",
                entity_name or self.__entity_name,
                {
                    "options": ids
                }
            )
        except Exception as error:
            error_detected = error
            return False

        return True

    def select_func(self, query, data):
        """Mehtod call function """
        result = True
        try:
            query_result = self.execute_func(query, data)

        except Exception as error:
            return False

        for row in query_result:
            response = dict(row)
            function_name = [a for a in response]
            if 'error' in response[function_name[0]]:
                print("ERROR - composer.config_filters_compose" +
                      "-Insert to filter: "
                      + response[function_name[0]])
                result = False

        return result

    def execute_func(self, query, data):
        """Mehtod execute function update filters"""
        context = self.__context
        session = context.session()
        statement = SqlalchemyUtils().query_execute_function(query, data)
        with session as connection:
            query_result = connection.execute(statement)

        return query_result

    def execute_statement(self, statement):
        """Mehtod execute function update filters"""
        context = self.__context
        session = context.session()
        with session as connection:
            query_result = connection.execute(statement)

        return query_result

    def execute_statement_entity(self, statement , entity_name = None ):
        """Mehtod execute function compose with the 
           entity_info
        """
        context = self.__context
        session = context.session()
        entity_name = entity_name or self.__entity_name
        entity_info = EntityUtils.get_entity_definition(entity_name)
        schema = context._PostgreSqlContext__configurations['schema']
        table = entity_info['tableName']
        statement = f'{statement} "{schema}".{table}' 
        with session as connection:
            query_result = connection.execute(statement)

        return query_result

    def context(self):
        return self.__context

    def entity_name(self):
        """Get the entity name

        Returns:
            string: The entoty name
        """
        return self.__entity_name
