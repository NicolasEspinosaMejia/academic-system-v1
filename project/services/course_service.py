import json
from datetime import date

from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils
from project.services.service import Service


class CourseService(Service):

    def __init__(self, compose, repository):
        self.compose = compose
        self.repository = repository
        Service.__init__(self, compose)

    def get_course(self):
        """This endpoint has the functionality of bringing all the course
           created in the system.

        Returns:
            [list]: This answer refers to a list of courses
        """
        result = {
            "data": [],
            "details": ""
        }

        result["data"] = self.compose.get_course()

        return result

    def manage_course(self, data):
        """This endpoint is in charge of managing the courses of the academy,
           through an action that they carry out

        Args:
            data (dict): This attribute refers to the base structure that a
                         course needs to enter the academy.
        """
        result = {
            "data": [],
            "details": ""
        }

        if not isinstance(data, dict):
            raise TypeError(
                "The 'data' is not in the correct format")

        if not self.check_data_manage_course(data):
            raise ValueError(
                "The validation does not meet the minimum requirements")

        data = self.data_cleaning(data)

        action_value = data["action"]
        del data["action"]

        if not self.check_data_time(data):
            raise ValueError(
                "The courses do not have consistent dates")

        response = self.compose.manage_course_add(data) \
            if action_value == "add" else \
                self.compose.manage_course_upd(data)

        if response is not None:
            result["details"] = "Successfully configured course"

        return result

    def manage_course_delete(self, data):
        """This endpoint is in charge of managing the courses of the academy,
           through an action that they carry out

        Args:
            data (dict): This attribute refers to the base structure that a
                         course needs to enter the academy.
        """
        result = {
            "data": [],
            "details": ""
        }

        if not isinstance(data, dict):
            raise TypeError(
                "The 'data' is not in the correct format")

        if not self.check_data_manage_course_delete(data):
            raise ValueError(
                "The validation does not meet the minimum requirements")

        response = self.compose.manage_course_del(data)

        if response is not None:
            result["details"] = "Successfully removed course"

        return result

    def check_data_manage_course_delete(self, data):
        """[summary]

        Args:
            data ([type]): [description]
        """
        result = True

        if "identifier"not in data or\
           not isinstance(data["identifier"], int):
            result = False

        return result

    def data_cleaning(self, data):
        """This endpoint is in charge of cleaning the data depending
           on the action taken

        Args:
            data (dict): This attribute refers to a dictionary
                           of type course

        Returns:
            [dict]: Returns a dictionary, with the corrected data
        """
        course_start_date = data["courseStartDate"].split("/")

        data["courseStartDate"] =\
            date(int(course_start_date[0]),
                 int(course_start_date[1]),
                 int(course_start_date[2])).isoformat()

        course_end_date = data["courseEndDate"].split("/")

        data["courseEndDate"] =\
            date(int(course_end_date[0]),
                 int(course_end_date[1]),
                 int(course_end_date[2])).isoformat()

        return data

    def check_data_time(self, data):
        """This endpoint verifies the dates of the courses

        Args:
            data (bool): Returns a flag to define whether or not
                         I pass the validations
        """
        result = True

        if data["courseEndDate"] <= data["courseStartDate"]:
            result = False

        return result

    def check_data_manage_course(self, data):
        """This method is in charge of performing a check on the
           attributes that the methods that use it must have mandatory

        Args:
            data (dict): This attribute refers to a dictionary, which
                         contains the configuration attributes for validations

        Returns:
            [dict]: Returns an element already constituted to send to the stored procedure
        """
        result = True

        if "nameCourse" not in data or\
           not isinstance(data["nameCourse"], str):
            result = False

        if "courseStartDate" not in data or\
           not isinstance(data["courseStartDate"], str):
            result = False

        if "courseEndDate" not in data or\
           not isinstance(data["courseEndDate"], str):
            result = False

        if "action" not in data or\
           not isinstance(data["action"], str) and\
           data["action"] not in ("add", "del", "upd"):
            result = False

        return result