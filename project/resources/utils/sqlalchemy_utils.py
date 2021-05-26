import json
import operator
from datetime import datetime
from re import sub

from sqlalchemy import MetaData, Table, func, select, Boolean, DateTime, Float,\
    Integer, String, or_, and_, not_, ForeignKey, Date, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import exists, ColumnCollection
from sqlalchemy.sql import text
from sqlalchemy.sql.functions import Function
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.selectable import Select
from project.models.models import TimeStamp
from project.resources.utils.entity_utils import EntityUtils
from project.resources.utils.generals_utils import GeneralsUtils

SCHEMA_TYPES_BY_SQLALCHEMY_FUNCTIONS = {
    "boolean": Boolean,
    "dateTime": DateTime,
    "integer": Integer,
    "number": Float,
    "object": JSONB,
    "string": String
}
OPERATOR_MAP = {
    "=": operator.eq,
    "==": operator.eq,
    "equals": operator.eq,
    "eq": operator.eq,
    "!=": operator.ne,
    "<>": operator.ne,
    "ne": operator.ne,
    "notequals": operator.ne,
    "<": operator.lt,
    "lt": operator.lt,
    ">": operator.gt,
    "gt": operator.gt,
    "<=": operator.le,
    "le": operator.le,
    ">=": operator.ge,
    "ge": operator.ge
}
UDF_DATA_TYPES = {
    ('number', None): BigInteger,
    ('number', 0): BigInteger,
    ('string', None): String,
    ('boolean', None): Boolean,
    ('date', None): Date,
    ('datetime', None): TimeStamp,
}


class SqlalchemyUtils:
    @staticmethod
    def configure_table(entity_name, meta_data):
        if not GeneralsUtils.validate_string(entity_name) or \
                not isinstance(meta_data, MetaData):
            raise Exception

        definition = EntityUtils.get_entity_definition(entity_name).copy()

        if "tableName" not in definition:
            raise Exception

        table_sqlalchemy = Table(definition["tableName"], meta_data)

        if not GeneralsUtils.validate_attribute(
            "properties",
            definition,
            dict
        ):
            raise Exception

        [definition.setdefault(key, {}) for key in ['primaryKey', 'uniques',
                                                    'foreignKeys']]
        foreign_keys = {}
        for k, foreign_key in definition['foreignKeys'].items():
            foreign_key_entity, field = foreign_key.split(".")
            table_name = EntityUtils.get_entity_definition(
                foreign_key_entity)['tableName']
            foreign_keys[k] = f'{table_name}.{field}'

            if f'{meta_data.schema}{table_name}' not in meta_data.tables:
                SqlalchemyUtils.configure_table(foreign_key_entity, meta_data)

        for item_key, item_value in definition["properties"].items():
            if "type" not in item_value or \
                    not GeneralsUtils.validate_attribute(
                        item_value["type"],
                        SCHEMA_TYPES_BY_SQLALCHEMY_FUNCTIONS):
                raise Exception

            column_sqlalchemy = Column(
                item_value["dbName"],
                SCHEMA_TYPES_BY_SQLALCHEMY_FUNCTIONS[item_value["type"]],
                *([ForeignKey(foreign_keys[item_key])] if
                  item_key in foreign_keys else []),
                primary_key=item_key in definition["primaryKey"],
                unique=item_key in definition["uniques"])

            table_sqlalchemy.append_column(column_sqlalchemy)

        return table_sqlalchemy

    @staticmethod
    def generate_select_statement(entity_name, table_sqlalchemy, options):
        if not isinstance(table_sqlalchemy, Table) or\
           not isinstance(options, dict):
            raise Exception
        columns = ColumnCollection(*table_sqlalchemy.c)

        if not isinstance(entity_name, str):
            raise Exception("The entity name has not been configured")
        entity_definition = EntityUtils.get_entity_definition(entity_name)

        statement = select(list(columns))

        if 'json' in options:
            for json_field in options['json']:
                SqlalchemyUtils.handle_json(
                    columns, json_field['field'], table_sqlalchemy,
                    entity_name, json_field['column'],
                    data_type_name=json_field.get('data_type_name'),
                    precision=json_field.get('precision'))

        if 'udfs' in options:
            SqlalchemyUtils.handle_udfs(columns, options, table_sqlalchemy)
            tables = {udf['entity_name']: SqlalchemyUtils.configure_table(
                udf['entity_name'], table_sqlalchemy.metadata)
                for udf in options['udfs']}

            statement = select(list(columns))

            select_from = table_sqlalchemy
            for entity_name, table in tables.items():
                foreign_key = list(table.foreign_keys)[0]
                udf = next(iter(u for u in options['udfs'] if
                                u['entity_name'] == entity_name))
                on_clause = and_(
                    foreign_key.parent == foreign_key.column,
                    getattr(columns, udf['map_id_key']) == udf['map_id'])
                select_from = select_from.join(table, on_clause, True)
            statement = statement.select_from(select_from)

        if "group_by" in options:
            group_by_attributes = options["group_by"]

            if not GeneralsUtils.validate_attribute(
                "column_name",
                group_by_attributes,
                str
            ):
                raise Exception("")

            column_db_name = EntityUtils.translate_attribute_name(
                entity_definition=entity_definition,
                property_name=group_by_attributes["column_name"])

            column_sqlalchemy = getattr(columns, column_db_name)

            statement = statement.with_only_columns(
                [column_sqlalchemy, func.count(column_sqlalchemy)]).group_by(column_db_name)

        if 'filters' in options:
            statement = statement.where(SqlalchemyUtils.handle_filters(
                entity_definition, options, columns))

        if "distinct" in options:
            column_db_name, column_name = None, options["distinct"]

            if column_name is not None:
                if not GeneralsUtils.validate_string(column_name) or \
                        column_name not in entity_definition["properties"]:
                    raise Exception

                column_db_name = EntityUtils.translate_attribute_name(
                    entity_definition=entity_definition,
                    property_name=column_name)

            statement = statement.distinct(column_db_name) if column_db_name \
                else statement.distinct()

        if "order_by" in options:
            order_by_items = options["order_by"]
            message_error, fail, error_detected = '', False, None

            if isinstance(order_by_items, dict):
                order_by_items = [order_by_items]

            if not isinstance(order_by_items, list):
                raise Exception("")

            for order_by_item in order_by_items:
                if not GeneralsUtils.validate_attribute("column_name",
                                                        order_by_item, str):
                    error_detected = "'Column name' not present in 'order by' parameters"
                    fail = True
                    break

                try:
                    column_sqlalchemy = getattr(
                        columns,
                        EntityUtils.translate_attribute_name(
                            entity_definition=entity_definition,
                            property_name=order_by_item["column_name"]))

                except Exception as error:
                    error_detected = error
                    message_error = ""
                    fail = True
                    break

                if not GeneralsUtils.\
                   validate_attribute("desc", order_by_item):
                    statement = statement.order_by(column_sqlalchemy.asc())
                    break

                if not isinstance(order_by_item["desc"], bool):
                    message_error = ""
                    fail = True
                    break

                if order_by_item["desc"]:
                    statement = statement.order_by(column_sqlalchemy.desc())

                else:
                    statement = statement.order_by(column_sqlalchemy.asc())

            if fail:
                raise Exception("", message_error, error_detected)

        if "paginate" in options:
            options_paginate = options["paginate"]
            if not GeneralsUtils.\
                   validate_attribute("offset", options_paginate, int) or\
               not GeneralsUtils.\
                   validate_attribute("limit", options_paginate, int) or\
               options["paginate"]["offset"] < 0 or\
               options["paginate"]["limit"] < 1:
                raise Exception("")

            statement = statement.limit(
                options["paginate"]["limit"]).\
                offset(options["paginate"]["offset"])

        return statement

    @staticmethod
    def handle_udfs(columns, options, table_sqlalchemy):
        """Sets up statement base on option UDFs.

            Args:
                columns (ColumnCollection): SQLAlchemy column collection
                options (dict): Options
                table_sqlalchemy (Table): SQLAlchemy table
        """
        tables = {udf['entity_name']: SqlalchemyUtils.configure_table(
            udf['entity_name'], table_sqlalchemy.metadata)
            for udf in options['udfs']}

        for udf in options['udfs']:
            map_id_col_name = EntityUtils.translate_attribute_name(
                entity_name=udf['entity_name'], property_name=udf['map_id_key'])
            columns.add(getattr(tables[udf['entity_name']].c, map_id_col_name).
                        label(udf['map_id_key']))

            for config in udf['map']:
                label = f'{config["number"]} {config["name"]} ' \
                        f'{udf["entity_field_name"]}'

                SqlalchemyUtils.handle_json(
                    columns, label, tables[udf['entity_name']],
                    udf['entity_name'], udf['value_key'],
                    data_type_name=config["dataType"],
                    precision=config.get("precision"))

    @staticmethod
    def handle_json(columns, label, table, entity_name, property_name,
                    data_type=String, data_type_name=None, precision=None):
        """Extracts JSON column fields into columns of their own.

        Args:
            columns (ColumnCollection): Query column collection
            label (str): JSON column field key
            table (Table): SQLAlchemy table
            entity_name (str): Entity name
            property_name (str): Entity property's name
            data_type (Integer|String|Boolean|Date|DateTime):
            data_type_name (str): One of number, string, boolean, date,
                datetime
            precision (int): Amount of decimals
        """
        if data_type_name:
            data_type = UDF_DATA_TYPES.get((data_type_name, precision), Float)

        value_col_name = EntityUtils.translate_attribute_name(
            entity_name=entity_name, property_name=property_name)
        value = getattr(table.c, value_col_name)
        columns.add(value[label].astext.cast(data_type).label(label))

    @staticmethod
    def handle_filters(entity_definition, options, columns):
        """Sets up statement base on option filters.

        In the 'filters' entry of the options dictionary, there can only be one
        type of logical operator string ('and' or 'or') between clauses in a
        same nesting level, if have you need to mix both logical operators in
        the same condition you MUST introduce a new nesting group, i.e., a new
        list with only one operator type string,
        e.g.:
            Given A, B, C clauses in a condition logicality related as
            A OR B AND C,
            this is wrong:
            - [A, 'or', B, 'and' C],
            this is right:
            - [A, 'or', [B, 'and, C]] if you want to preserve the logical
            operator precedence evaluation (AND operands are evaluated first)
            - [[A, 'or', B], 'and, C]] if you want to override the logical
            operator precedence evaluation
        And so this must be for the indefinitely amount of nesting levels.

        Args:
            entity_definition (dict): Entity definition
            options (dict): Options
            statement (statement): SQLAlchemy statement
            columns (ColumnCollection): SQLAlchemy Table's column collection

        Returns: SQLAlchemy statement
        """
        items = options.get('filters')
        if not items:
            return and_()
        items = [items] if isinstance(items[0], str) and items else items

        logical_operator = items[1] if len(items) > 1 else 'and'
        if logical_operator not in ('and', 'or'):
            raise Exception(f'Unidentified logical operator {logical_operator}')

        clauses = []
        for item in items[::2]:
            if item[1] in ('and', 'or'):
                options = {'filters': item}
                item = SqlalchemyUtils.handle_filters(entity_definition,
                                                      options, columns)
                clauses.append(item)
                continue

            item[0] = sub('(/_|/%|//)', lambda x: x.group(0)[1], item[0])

            attribute_name = EntityUtils.translate_attribute_name(
                entity_definition=entity_definition,
                property_name=item[0])
            column = getattr(columns, attribute_name)

            if isinstance(columns[attribute_name].type, (DateTime, TimeStamp)) \
                    and not isinstance(item[2], (Column, datetime)):
                item[2] = GeneralsUtils.try_parse_date_time(item[2])

            if isinstance(item[2], (str, tuple, Select, list)) or \
                    item[1] in {'in', 'exists'}:
                if item[1] in {'=', '==', 'equals', 'eq'}:
                    clauses.append(column.like(item[2], escape='/'))
                elif item[1] == "contains":
                    clauses.append(column.contains(item[2], escape='/'))
                elif item[1] == "notcontains":
                    clauses.append(not_(column.contains(item[2], escape='/')))
                elif item[1] in {'notequals', '!=', '<>'}:
                    clauses.append(column.notlike(item[2], escape='/'))
                elif item[1] == "startswith":
                    clauses.append(column.startswith(item[2], escape='/'))
                elif item[1] == "endswith":
                    clauses.append(column.endswith(item[2], escape='/'))
                elif item[1] == "in":
                    clauses.append(column.in_(item[2]))
                elif item[1] == "exists":
                    foreign_key = item[2]['fk_prop'] or attribute_name
                    foreign_key = getattr(item[2]['subquery'].froms[0].c,
                                          foreign_key)
                    clauses.append(exists(item[2]['subquery'].where(
                        column == foreign_key)))
                else:
                    raise Exception(f'Unidentified clause operator: {item[1]}')

            elif isinstance(item[2], (int, float, datetime, Column)):
                clauses.append(OPERATOR_MAP[item[1]](column, item[2]))

        return or_(*clauses) if logical_operator == 'or' else and_(*clauses)

    @staticmethod
    def query_execute_function(query, data):
        """Get query execute function"""
        if isinstance(query, str):
            if data is None:
                statement = text(query)
            else:
                statement = text(query).bindparams(**data)
        return statement

    @staticmethod
    def generate_where_statement(entity_name,
                                 options,
                                 statement,
                                 table_sqlalchemy):
        """ This method does a where, using multiple primary keys. """

        if not isinstance(entity_name, str):
            raise Exception("The entity name has not been configured.")

        if not isinstance(options['options'], dict):
            raise Exception("The entity options is not valid.")

        if not isinstance(statement, object):
            raise Exception("The statement is not valid.")

        entity_definitions = EntityUtils.get_entity_definition(entity_name)

        for key in options['options']:
            column_sqlalchemy = getattr(
                        table_sqlalchemy.columns,
                        EntityUtils.translate_attribute_name(
                            entity_definition=entity_definitions,
                            property_name=key))
            statement = statement.where(column_sqlalchemy ==
                                        options['options'][key])

        return statement

    @staticmethod
    def generate_update_statement(entity_name, table_sqlalchemy, options,
                                  values):
        new_values = dict(filter(lambda x: '.' not in x[0], values.items()))
        new_values = EntityUtils.get_editables_values(entity_name, new_values,
                                                      True)

        fields = dict(filter(lambda x: '.' in x[0], values.items()))
        where, new_fields = [], {}
        for key, value in fields.items():
            property, field = key.split('.')
            column_name = EntityUtils.translate_attribute_name(
                entity_name, property_name=property)
            table_col = getattr(table_sqlalchemy.c, column_name)
            new_value = new_fields.get(column_name, table_col)

            if 'json' in options:
                for json_option in options['json']:
                    if 'rename' in json_option:
                        new_value = func.jsonb_set(
                            new_value, '{%s}' % json_option['rename'],
                            new_value[field])

                    if 'cast' in json_option:
                        if json_option['cast'] == 'number' and json_option.get(
                                'cast_from') in ('date', 'datetime'):
                            number_format = '9909909999' if \
                                json_option['cast_from'] == 'date' \
                                else '9909909999099099'
                            value = func.to_jsonb(func.to_number(
                                table_col[field].astext, number_format))
                        else:
                            data_type = UDF_DATA_TYPES.get(
                                (json_option['cast'], None), Float)
                            value = func.to_jsonb(
                                table_col[field].astext.cast(data_type))

                    where.append(table_col[field].isnot(None))

            value = value if isinstance(value, (Function, type(None))) else \
                json.dumps(value)
            new_fields[column_name] = new_value.op('-')(field) \
                if value is None else func.jsonb_set(
                new_value, '{%s}' % field, value)

        statement = table_sqlalchemy.update().values(**new_values, **new_fields)
        statement = statement.where(*where) if where else statement

        if not isinstance(entity_name, str):
            raise Exception("The entity name has not been configured")

        columns = ColumnCollection(*table_sqlalchemy.c)
        if 'udfs' in options:
            for udf in options['udfs']:
                map_filter = [udf['map_id_key'], '=', udf['map_id']]
                options['filters'] = [map_filter, 'and'] + options['filters'] \
                    if options.get('filters') else [map_filter]

            SqlalchemyUtils.handle_udfs(columns, options, table_sqlalchemy)

        if 'filters' in options:
            entity_definition = EntityUtils.get_entity_definition(entity_name)
            statement = statement.where(SqlalchemyUtils.handle_filters(
                entity_definition, options, columns))

        return statement
