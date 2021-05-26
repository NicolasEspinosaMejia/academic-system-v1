import json
from datetime import date

from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils
from project.services.service import Service


class AddressService(Service):


    __DICTIONARY__ = {
        "gender": {
            "undefined": 1,
            "male": 2,
            "femenine": 3
        }
    }

    def __init__(self, compose, repository):
        self.compose = compose
        self.repository = repository
        Service.__init__(self, compose)

    def get_address(self):
        """This endpoint has the functionality of bringing all the addresss
           created in the system.

        Returns:
            [list]: This answer refers to a list of addresss
        """
        result = {
            "data": [],
            "details": ""
        }

        result["data"] = self.compose.get_address()

        return result

    def manage_address(self, data):
        """This endpoint is in charge of managing the addresss of the academy,
           through an action that they carry out

        Args:
            data (dict): This attribute refers to the base structure that a
                         address needs to enter the academy.
        """
        result = {
            "data": [],
            "details": ""
        }

        if not isinstance(data, dict):
            raise TypeError(
                "The 'data' is not in the correct format")

        if not self.check_data_manage_address(data):
            raise ValueError(
                "The validation does not meet the minimum requirements")

        action_value = data["action"]
        del data["action"]

        response = self.compose.manage_address_add(data) \
            if action_value == "add" else \
                self.compose.manage_address_upd(data)

        if response is not None:
            result["details"] = "Successfully configured address"

        return result

    def manage_address_delete(self, data):
        """This endpoint is in charge of managing the addresss of the academy,
           through an action that they carry out[summary]

        Args:
            data (dict): This attribute refers to the base structure that a
                         address needs to enter the academy.
        """
        result = {
            "data": [],
            "details": ""
        }

        if not isinstance(data, dict):
            raise TypeError(
                "The 'data' is not in the correct format")

        if not self.check_data_manage_address_delete(data):
            raise ValueError(
                "The validation does not meet the minimum requirements")

        response = self.compose.manage_address_del(data)

        if response is not None:
            result["details"] = "Successfully removed address"

        return result

    def check_data_manage_address(self, data):
        """This method is in charge of performing a check on the
           attributes that the methods that use it must have mandatory

        Args:
            data (dict): This attribute refers to a dictionary, which
                         contains the configuration attributes for validations

        Returns:
            [dict]: Returns an element already constituted to send to the stored procedure
        """
        result = True

        if "permanentAddress" not in data or\
           not isinstance(data["permanentAddress"], str):
            result = False

        if "typeAddress" not in data or\
           not isinstance(data["typeAddress"], int):
            result = False

        if "identifierStudent" not in data or\
           not isinstance(data["identifierStudent"], int):
            result = False

        if "student" not in data or\
           not isinstance(data["student"], dict):
            result = False

        if "action" not in data or\
           not isinstance(data["action"], str) and\
           data["action"] not in ("add", "del", "upd"):
            result = False

        if "identifier" in data and\
           data["action"] == "add" and\
           not isinstance(data["identifier"],int):
            result = False

        return result

    def check_data_manage_address_delete(self, data):
        """This method is in charge of performing a check on the
           attributes that the methods that use it must have mandatory

        Args:
            data (dict): This attribute refers to a dictionary, which
                         contains the configuration attributes for validations

        Returns:
            [dict]: Returns an element already constituted to send to the stored procedure
        """
        result = True

        if "identifier" not in data or\
           not isinstance(data["identifier"], int) or\
           data["identifier"] == 0:
            result = False

        return result


