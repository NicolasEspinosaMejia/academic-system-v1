import json
from datetime import date

from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils
from project.services.service import Service


class StudentService(Service):

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

    def get_student(self):
        """This endpoint has the functionality of bringing all the students
           created in the system.

        Returns:
            [list]: This answer refers to a list of students
        """
        result = {
            "data": [],
            "details": ""
        }

        result["data"] = self.compose.get_student()

        return result

    def manage_student(self, data):
        """This endpoint is in charge of managing the students of the academy,
           through an action that they carry out

        Args:
            data (dict): This attribute refers to the base structure that a
                         student needs to enter the academy.
        """
        result = {
            "data": [],
            "details": ""
        }

        if not isinstance(data, dict):
            raise TypeError(
                "The 'data' is not in the correct format")

        if not self.check_data_manage_student(data):
            raise ValueError(
                "The validation does not meet the minimum requirements")

        data = self.data_cleaning(data)

        action_value = data["action"]
        del data["action"]

        response = self.compose.manage_student_add(data) \
            if action_value == "add" else \
                self.compose.manage_student_upd(data)

        if response is not None:
            result["details"] = "Successfully configured student"

        return result

    def manage_student_delete(self, data):
        """This endpoint is in charge of managing the students of the academy,
           through an action that they carry out[summary]

        Args:
            data (dict): This attribute refers to the base structure that a
                         student needs to enter the academy.
        """
        result = {
            "data": [],
            "details": ""
        }

        if not isinstance(data, dict):
            raise TypeError(
                "The 'data' is not in the correct format")

        if not self.check_data_manage_student_delete(data):
            raise ValueError(
                "The validation does not meet the minimum requirements")

        response = self.compose.manage_student_del(data)

        if response is not None:
            result["details"] = "Successfully removed student"

        return result

    def check_data_manage_student(self, data):
        """This method is in charge of performing a check on the
           attributes that the methods that use it must have mandatory

        Args:
            data (dict): This attribute refers to a dictionary, which
                         contains the configuration attributes for validations

        Returns:
            [dict]: Returns an element already constituted to send to the stored procedure
        """
        result = True

        if "studentName" not in data or\
           not isinstance(data["studentName"], str):
            result = False

        if "studentLastName" not in data or\
           not isinstance(data["studentLastName"], str):
            result = False

        if "birthDate" not in data or\
           not isinstance(data["birthDate"], str):
            result = False

        if "gender" not in data or\
           not isinstance(data["gender"], str):
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

    def check_data_manage_student_delete(self, data):
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

    def data_cleaning(self, data):
        """[summary]

        Args:
            data ([type]): [description]
        """
        data["gender"] =\
            self.__DICTIONARY__["gender"][data["gender"]]

        birth_date_time = data["birthDate"].split("/")

        data["birthDate"] =\
            date(int(birth_date_time[0]),
                 int(birth_date_time[1]),
                 int(birth_date_time[2])).isoformat()

        return data
