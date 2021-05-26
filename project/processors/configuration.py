from project.configuration_manager import ConfigurationManager
from project.models.queue_message_model import QueueMessageModel


class Configuration():

    def exe(self, data):
        print(data)

        microservice = ConfigurationManager.microservice

        microservice.sender_queue_service_client.send_message(
            ConfigurationManager.get_config("QUEUE_INTEROPERABILITY_NAME"),
            QueueMessageModel(
                "Interoperability",
                "PAP-COM-configuration.exe",
                ["Hi again"]))

        return True
