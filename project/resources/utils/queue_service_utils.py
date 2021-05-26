from logging import error
from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils


class QueueServiceUtils():

    @staticmethod
    def check_message_attributes(message):
        fail = None
        required_attributes =\
            [attribute for attribute in
             Constants.QUEUE_MESSAGE_ATTRIBUTES
             if attribute["REQUIRED"]]

        for required_attribute in required_attributes:
            if required_attribute["NAME"] not in message:
                fail = True
                break

        return False if fail is True else True

    @staticmethod
    def check_message_event_type(message):
        queue_message_event_type_key =\
            Constants.QUEUE_MESSAGE_EVENT_TYPE_KEY

        if queue_message_event_type_key not in message:
            return False

        event_type_split =\
            QueueServiceUtils.\
            split_message_event_type(message[queue_message_event_type_key])

        if len(event_type_split) != 4:
            return False

        return True

    @staticmethod
    def get_message_event_type_by_method_name(language, version, method_name):
        queue_message_event_types = Constants.QUEUE_MESSAGE_EVENT_TYPES

        if language not in queue_message_event_types or\
           version not in queue_message_event_types[language] or\
           method_name not in queue_message_event_types[language][version]:
            raise ValueError(
                "The event type required was not found. " +
                f"Parameters: {language}, " +
                f"{version}, " +
                f"{method_name}")

        return queue_message_event_types[language][version][method_name]

    @staticmethod
    def split_message_event_type(event_type):
        result = []

        if not isinstance(event_type, str):
            return []

        result = event_type.split("-")

        if len(result) != 3:
            return []

        result.extend(result[2].split("."))
        result.remove(result[2])

        if len(result) != 4:
            return []

        return result

    @staticmethod
    def set_global_data_attributes(message):
        event_type_split = QueueServiceUtils.split_message_event_type(
            message[Constants.QUEUE_MESSAGE_EVENT_TYPE_KEY])

        GeneralsUtils.set_global_data(
            Constants.QUEUE_MESSAGE_EVENT_TYPE_LANGUAGE_KEY,
            event_type_split[0])
        GeneralsUtils.set_global_data(
            Constants.QUEUE_MESSAGE_EVENT_TYPE_TYPE_KEY,
            event_type_split[1])
        GeneralsUtils.set_global_data(
            Constants.QUEUE_MESSAGE_EVENT_TYPE_ENTITY_KEY,
            event_type_split[2])
        GeneralsUtils.set_global_data(
            Constants.QUEUE_MESSAGE_EVENT_TYPE_ACTION_KEY,
            event_type_split[3])

        attributes = Constants.QUEUE_MESSAGE_ATTRIBUTES

        for attribute in attributes:
            if attribute["NAME"] in message:
                GeneralsUtils.set_global_data(
                    attribute["GLOBAL_DATA_KEY"], message[attribute["NAME"]])
