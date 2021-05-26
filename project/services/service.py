from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils


class Service():

    compose = None
    data = []

    def __init__(self, compose):
        self.data = []
        self.compose = compose
        self.__init_service__()

    def __init_service__(self):
        return

    def check_attributes(self, attributes: dict):
        """This method is in charge of validating the attributes that
           the request dictionary must contain

        Args:
            attributes (dict): This dictionary will contain the
                               attributes of externalSystemName,
                               connectionName and the devices.

        Returns:
            bool: device validation
        """
        result = True
        request_body_external_system_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_NAME_KEY
        request_body_external_system_connection_name_key =\
            Constants.REQUEST_BODY_EXTERNAL_SYSTEM_CONNECTION_NAME_KEY
        request_body_devices_key = "devices"

        if not isinstance(attributes, dict) or\
           not GeneralsUtils.check_dictionary_property(
                request_body_external_system_name_key, attributes) or\
           not GeneralsUtils.check_dictionary_property(
                request_body_external_system_connection_name_key, attributes) or\
           not GeneralsUtils.check_dictionary_property(
                request_body_devices_key, attributes) or\
           not GeneralsUtils.validate_list(
                attributes[request_body_devices_key]):
            result = False

        devices = attributes[request_body_devices_key]
        for device in list(devices):
            if not GeneralsUtils.check_dictionary_property(
               "deviceId", device):
                devices.remove(device)

        if len(devices) == 0:
            result = False

        return result
