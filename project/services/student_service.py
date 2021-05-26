import json

from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils
from project.services.service import Service


class StudentService(Service):


    def __init__(self, compose):
        self.compose = compose
        Service.__init__(self, compose)

    def get_student(self, data):
        print(data)

    def manage_student(self, data):
        """This endpoint is in charge of managing the students of the academy,
           through an action that they carry out[summary]

        Args:
            data (dict): This attribute refers to the base structure that a
                         student needs to enter the academy.
        """
        result = {
            "data": [],
            "details": []
        }

        if not isinstance(data, dict):
            raise TypeError(
                "The 'data' is not in the correct format")

        if not self.check_data_manage_student(data):
            raise ValueError(
                "The validation does not meet the minimum requirements")

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

        if "studentLastName" not in data or\
           not isinstance(data["birthDate"], str):
            result = False

        if "studentLastName" not in data or\
           not isinstance(data["gender"], str):
            result = False

        if "studentLastName" not in data or\
           not isinstance(data["action"], str) and\
           data["action"] not in ("add", "del"):
            result = False

        return result
