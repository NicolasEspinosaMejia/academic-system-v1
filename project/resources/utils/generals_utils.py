import base64
import json
import os
import types
import yaml

from datetime import datetime

from project.constants import Constants


class GeneralsUtils:
    global_data = {}

    @staticmethod
    def __cast_attribute__(value):
        result = None
        primitive_data_types = (int, float, str, bool)

        if value is None or\
           isinstance(
                value,
                primitive_data_types):
            result = value

        elif isinstance(value, (list, tuple)):
            result = [GeneralsUtils.__cast_attribute__(item)
                      for item in value]

        elif isinstance(value, dict):
            result = {}
            for key in value:
                result[key] = GeneralsUtils.__cast_attribute__(value[key])

        elif isinstance(value, datetime):
            result = GeneralsUtils.try_parse_date_time(value)

        else:
            result = GeneralsUtils.instance_to_dict(value)

        return result

    @staticmethod
    def clean_dictionary(dictionary):
        if not isinstance(dictionary, dict):
            raise ValueError("A dictionary was expected")

        result = dict(dictionary)

        for key in dictionary:
            if result[key] is None:
                del result[key]

        return result

    @staticmethod
    def decode(data):
        return base64.b64decode(data).decode('utf-8')

    @staticmethod
    def encode(data):
        data_bytes = data.encode("ascii")
        data_encoded = base64.b64encode(data_bytes)
        return data_encoded

    @staticmethod
    def format_response_data(data):
        result = []

        if GeneralsUtils.validate_string(data) or\
           isinstance(data, (dict, int, float)):
            data = [data]

        elif isinstance(data, object) and not isinstance(data, list):
            data = [data.__dict__]

        if not isinstance(data, list):
            raise TypeError("The 'data' is not in the correct format")

        for datum in data:
            if isinstance(datum, (dict, int, float, list, str)):
                result.append(datum)

            elif isinstance(data, object):
                result.append(datum.__dict__)

        return result

    @staticmethod
    def get_datetime(format: str = None):
        result = datetime.today()

        if GeneralsUtils.validate_string(format) and\
           format.capitalize() == "Iso":
            result = datetime.today().isoformat()

        return result

    @staticmethod
    def get_global_data(key):
        if not GeneralsUtils.validate_string(key):
            raise TypeError("The 'key' is not in the correct format")

        if key not in GeneralsUtils.global_data:
            return None

        return GeneralsUtils.global_data[key]

    @staticmethod
    def get_request_data(request):
        result = request.get_data()

        if len(result) == 0:
            return None

        if request.is_json:
            result = json.loads(request.get_data())

        elif isinstance(request.data, str):
            result = request.data

        return result

    @staticmethod
    def read_file(path: str, output_type: str = "json"):
        result = None
        read_file_output_types = Constants.READ_FILE_OUTPUT_TYPES

        if not GeneralsUtils.validate_string(path):
            raise TypeError("The 'path' is not in the required format")

        if not os.path.isfile(path):
            raise FileNotFoundError("The requested file was not found")

        if output_type not in read_file_output_types:
            raise ValueError("The required file type was not recognized")

        with open(path, "r") as text_file:
            if output_type == "json":
                result = json.load(text_file)

            elif output_type == "yaml":
                result = yaml.safe_load(text_file)

        return result

    @staticmethod
    def set_global_data(key, value):
        if not GeneralsUtils.validate_string(key):
            raise TypeError("The 'key' is not in the correct format")

        GeneralsUtils.global_data[key] = value

    @staticmethod
    def check_dictionary_property(
            key: str,
            dictionary: str):
        if not GeneralsUtils.validate_string(key) or\
           not isinstance(dictionary, dict):
            raise TypeError("Parameters are not in the correct format")

        if key not in dictionary:
            return False

        return True

    @staticmethod
    def instance_to_dict(instance):
        result = {}

        for attribute_name in dir(instance):
            if attribute_name[:2] == "__":
                continue

            attribute_value = getattr(instance, attribute_name)

            if isinstance(attribute_value, types.FunctionType) or\
               isinstance(attribute_value, types.MethodType):
                continue

            result[attribute_name] =\
                GeneralsUtils.__cast_attribute__(attribute_value)

        return result

    @staticmethod
    def validate_list(value) -> bool:
        if not isinstance(value, list):
            return False

        if len(value) == 0:
            return False

        return True

    @staticmethod
    def validate_string(value) -> bool:
        if not isinstance(value, str):
            return False

        if str.strip(value) == "":
            return False

        return True


    @staticmethod
    def validate_attribute(attribute_name,
                           structure,
                           attribute_types_allowed=None):
        result = False

        if not GeneralsUtils.validate_string(attribute_name) or\
           not isinstance(structure, (dict, tuple, list)) or\
           attribute_name not in structure:
            return False

        if attribute_types_allowed is None:
            result = True

        elif isinstance(attribute_types_allowed, type) or\
                (
                    isinstance(attribute_types_allowed, tuple) and
                    all(isinstance(type_attribute_allowed, type)
                        for type_attribute_allowed in attribute_types_allowed)
                ):

            if isinstance(structure, dict):
                attribute = structure[attribute_name]
            else:
                attribute =\
                    next(item for item in structure if attribute_name == item)

            if isinstance(attribute, attribute_types_allowed):
                result = True

        else:
            return False

        return result

    @staticmethod
    def try_parse_date_time(value, format="%Y-%m-%dT%H:%M:%SZ"):
        result = None
        date_time_formats = Constants.DATE_TIME_FORMATS

        if format not in date_time_formats:
            raise ValueError("No valid date format")

        result = value.strptime(format)

        return result
