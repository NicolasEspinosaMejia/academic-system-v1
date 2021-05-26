from project.configuration_manager import ConfigurationManager
from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils


class ResponseDetailModel:

    def __init__(self,
                 message: str,
                 values: list = None,
                 level: str = None):
        response_body_detail_levels_enum =\
            Constants.RESPONSE_BODY_DETAIL_LEVELS_ENUM

        if level is None:
            level = response_body_detail_levels_enum[1]

        level = str(level).capitalize()
        if level not in response_body_detail_levels_enum:
            level = None

        if not isinstance(message, str) or\
           not isinstance(values, list) or\
           not isinstance(level, str):
            raise TypeError(
                    "The 'details' does not comply with the required format")

        self.message = message
        self.values = values
        self.level = level

    def to_dict(self):
        result = {
            "message": self.message,
            "values": self.values,
            "level": self.level}
        return result


class ResponseDataModel:

    data = []
    details: list = []

    def add_detail(self, message, values: list = [], level: str = None):
        detail = ResponseDetailModel(message, values, level)
        self.details.append(detail)

    def set_data(self, data):
        response_body_data_key = Constants.RESPONSE_BODY_DATA_KEY
        response_body_details_key = Constants.RESPONSE_BODY_DETAILS_KEY
        response_body_details_level_key =\
            Constants.RESPONSE_BODY_DETAILS_LEVEL_KEY
        response_body_details_message_key =\
            Constants.RESPONSE_BODY_DETAILS_MESSAGE_KEY
        response_body_details_values_key =\
            Constants.RESPONSE_BODY_DETAILS_VALUES_KEY

        if response_body_data_key not in data:
            data[response_body_data_key] = []

        if not isinstance(data[response_body_data_key], list):
            raise TypeError(
                    f"The '{response_body_data_key}' " +
                    "does not comply with the required format")

        if response_body_details_key not in data:
            data[response_body_details_key] = []

        if not isinstance(data[response_body_details_key], list):
            raise TypeError(
                    f"The '{response_body_details_key}' " +
                    "does not comply with the required format")

        self.data = data[response_body_data_key]

        fail = None
        self.details = []
        for data_detail in data[response_body_details_key]:
            try:
                self.add_detail(
                    message=data_detail[response_body_details_message_key],
                    values=data_detail[response_body_details_values_key],
                    level=data_detail[response_body_details_level_key])

            except Exception:
                fail = True
                break

        if fail:
            raise AttributeError("Error converting response details")

    def __verify_details__(self, details) -> bool:
        if isinstance(details, list) and\
           len([detail
                for detail in details
                if isinstance(detail, ResponseDetailModel)]) == 0:
            return True

        else:
            return False


class ResponseBodyModel(ResponseDataModel):

    def __init__(
            self,
            method: str,
            status_code: int,
            data: list = None,
            details: list = None):
        self.api_version = ConfigurationManager.get_api_version()
        self.method = method
        self.status_code = status_code

        if data is None:
            data = []

        if not isinstance(data, list):
            raise TypeError(
                    "The 'data' does not comply with the required format")
        self.data = data

        if details is None:
            details = []

        if not self.__verify_details__(details):
            raise TypeError(
                    "The 'details' does not comply with the required format")
        self.details = details

    api_version = None
    data = None
    method = None
    status_code = None
    transaction_id = None

    def set_status_code(self, value: int):
        if isinstance(value, int):
            self.status_code = value

    def to_dict(self):
        response_body_api_version_key = Constants.RESPONSE_BODY_API_VERSION_KEY
        response_body_data_key = Constants.RESPONSE_BODY_DATA_KEY
        response_body_details_key = Constants.RESPONSE_BODY_DETAILS_KEY
        response_body_method_key = Constants.RESPONSE_BODY_METHOD_KEY
        response_body_status_code_key = Constants.RESPONSE_BODY_STATUS_CODE_KEY
        response_body_transaction_id_key =\
            Constants.RESPONSE_BODY_TRANSACTION_ID_KEY

        result = {
            response_body_api_version_key: self.api_version,
            response_body_data_key: self.data,
            response_body_method_key: self.method,
            response_body_status_code_key: self.status_code,
            response_body_transaction_id_key: self.transaction_id}
        result_details = []

        for detail in self.details:
            result_details.append(
                detail.to_dict())
        result[response_body_details_key] = result_details

        return result
