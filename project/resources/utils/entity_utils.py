# encoding: utf-8
from project.configuration_manager import ConfigurationManager
from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils


class EntityUtils():

    @staticmethod
    def get_editables_values(entity_name, values, translate=False):
        if not isinstance(values, dict):
            return Exception

        entity_definition = EntityUtils.get_entity_definition(entity_name)
        result = values

        if "editables" not in entity_definition and translate:
            try:
                result = EntityUtils.translate_dictionary(
                    entity_definition=entity_definition,
                    entity_properties=result)

            except Exception as error:
                raise Exception("", error)

        elif "editables" in entity_definition:
            result = {}
            entity_properties_editables_keys =\
                entity_definition["editables"] +\
                list(Constants.CONFIGURATION_ENTITY_ATTRIBUTES)
            for entity_property in values:
                if entity_property in entity_properties_editables_keys:
                    key = entity_property
                    if translate:
                        key = EntityUtils.\
                            translate_attribute_name(
                                entity_definition=entity_definition,
                                property_name=entity_property
                            )
                    result[key] = values[entity_property]

        return result

    @staticmethod
    def get_entities_names(entities_parameters):
        ENTITIES_NAMES_KEYS = ("entity_1", "entity_2")
        result = {}

        if not isinstance(entities_parameters, dict):
            return result

        for entity_name_key in ENTITIES_NAMES_KEYS:
            if entity_name_key in entities_parameters:
                result[entity_name_key] = entities_parameters[entity_name_key]

        return result

    @staticmethod
    def get_entity_definition(entity_name):
        entity_definition = GeneralsUtils.\
            get_global_data("entity_definition_" + entity_name)

        if entity_definition is not None:
            return entity_definition

        entities_definitions = GeneralsUtils.\
            get_global_data("entities_definitions")

        if entities_definitions is None:
            entities_definitions_path = ConfigurationManager.get_config(
                "ENTITIES_DEFINITIONS_PATH")

            entities_definitions = GeneralsUtils.\
                read_file(entities_definitions_path)

            GeneralsUtils.set_global_data("entities_definitions",
                                          entities_definitions)

        if entity_name not in entities_definitions:
            raise Exception("Entity name not found in entities definitions")

        return entities_definitions[entity_name]

    @staticmethod
    def get_validation_schema(schema_name):
        validation_shemes_path = ConfigurationManager.get_config(
            "VALIDATION_SCHEMES_PATH")

        validation_shemes = GeneralsUtils.\
            read_file(validation_shemes_path)

        if schema_name not in validation_shemes:
            raise Exception(
                "The requested validation scheme could not be found")

        return validation_shemes[schema_name]

    @staticmethod
    def clean_config_attributes(entity):
        config_attributes = (
            Constants.ENTITY_ATTRIBUTE_TO_INSERT_KEY,
            Constants.ENTITY_ATTRIBUTE_WARNING_RESULT_KEY,
            Constants.ENTITY_ATTRIBUTE_OWNER_KEY,
            Constants.ENTITY_ATTRIBUTE_USER_CREATE_KEY,
            Constants.ENTITY_ATTRIBUTE_USER_UPDATE_KEY)

        for config_attribute in config_attributes:
            if config_attribute in entity:
                del entity[config_attribute]

        return entity

    @staticmethod
    def set_config_attributes(entity):
        entity[Constants.ENTITY_ATTRIBUTE_RESULT_KEY] = None
        entity[Constants.ENTITY_ATTRIBUTE_TO_INSERT_KEY] = None
        entity[Constants.ENTITY_ATTRIBUTE_WARNING_RESULT_KEY] = None
        entity[Constants.ENTITY_ATTRIBUTE_OWNER_KEY] = None

        return entity

    @staticmethod
    def translate_attribute_name(entity_name=None,
                                 entity_definition=None,
                                 column_name=None,
                                 property_name=None):
        if entity_definition is None:
            if entity_name is None:
                raise Exception("")

            entity_definition = EntityUtils.get_entity_definition(entity_name)

        if not GeneralsUtils.validate_attribute(
           "properties",
           entity_definition):
            raise Exception("")

        entity_properties = entity_definition["properties"]

        if GeneralsUtils.validate_string(column_name):
            for entity_property in entity_properties:
                if entity_properties[entity_property]["dbName"] == column_name:
                    return entity_property
            else:
                return column_name

        elif GeneralsUtils.validate_string(property_name):
            if GeneralsUtils.validate_attribute(
               property_name,
               entity_properties):
                return entity_properties[property_name]["dbName"]
            else:
                return property_name

        else:
            raise Exception

    @staticmethod
    def translate_dictionary(entity_name=None,
                             entity_definition=None,
                             table=None,
                             entity_properties=None):
        result = {}
        error_detected = None
        fail = True

        if entity_definition is None:
            if entity_name is None:
                raise Exception("")

            entity_definition = EntityUtils.get_entity_definition(entity_name)

        if isinstance(table, dict):
            for column_name in table:
                try:
                    property_name = EntityUtils.translate_attribute_name(
                        entity_definition=entity_definition,
                        column_name=column_name)
                    result[property_name] = table[column_name]

                except Exception as error:
                    raise Exception("", error)

            fail = False

        elif isinstance(entity_properties, dict):
            for property_name in entity_properties:
                try:
                    column_name = EntityUtils.translate_attribute_name(
                        entity_definition=entity_definition,
                        property_name=property_name)
                    result[column_name] = entity_properties[property_name]

                except Exception as error:
                    error_detected = error

                fail = False

        if fail:
            raise Exception("", error_detected)

        return result

    @classmethod
    def translate_obj_to_model(cls, obj, entity_name):
        definition = cls.get_entity_definition(entity_name)['properties']
        return {definition[k]['dbName']: v for k, v in obj.items()}

    @classmethod
    def translate_model_to_obj(cls, obj, entity_name):
        """Translates object's keys from database names to frontend ones.

        Args:
            obj (): Model instance dictionary
            entity_name (): Name of the entity object to consult the keys from.

        Returns:
            dict: Translated model entity dictionary
        """
        definition = cls.get_entity_definition(entity_name)['properties']
        return {k: obj[v['dbName']] for k, v in definition.items() if
                obj.get(v['dbName']) is not None}
