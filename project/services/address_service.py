import json

from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils
from project.services.service import Service


class AddressService(Service):


    def __init__(self, compose):
        self.compose = compose
        Service.__init__(self, compose)

    def get_address(self, data):
        print(data)

    def manage_address(self, data):
        print(data)
