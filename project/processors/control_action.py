from project.configuration_manager import ConfigurationManager
from project.composers.event_compose import EventCompose
from project.services.event_service import EventService


class ControlAction():

    def ocd(self, data: list) -> dict:
        """This methods is used when metering send the
        device update of yours states

        Args:
            data (list): the devices update in BD

        Returns:
            [type]: Return the devices was processed for
                    get_on_demand
        """
        data = data[0]
        configuration_data_success = []
        microservice = ConfigurationManager.microservice
        database_cache_repository = microservice.database_cache_repository
        sender_queue_service_client = microservice.sender_queue_service_client
        compose_event = EventCompose(
            database_cache_repository=database_cache_repository,
            sender_queue_service_client=sender_queue_service_client)
        service_event = EventService(
            compose=compose_event)

        configuration = \
            service_event.compose.get_configuration(data["transactionId"])
        for item in configuration["events"]:
            if item["result"]:
                configuration_data_success.append(item)

        for item in configuration_data_success:
            if self.search_device(data["deviceId"], item):
                configuration_data = item
                break

        data = {
            "events": [
                {
                    "externalSystemName":
                        configuration_data["externalSystemName"],
                    "connectionName": configuration_data["connectionName"],
                    "devices": configuration_data["devices"],
                    "eventTypeCodes": configuration_data["eventTypeCodes"]
                }
            ]
        }

        result = service_event.get_on_demand(data)

        return result

    def search_device(self,
                      devices: list,
                      configuration: list) -> bool:
        """This method is used for search the devices in
           the configuration that was extracted of redis

        Args:
            devices (list): the devices of metering
            configuration (list): configuration of redis

        Returns:
            list: Array of boolean with "all"
        """
        result = []
        for item in configuration["devices"]:
            if item["deviceId"] in devices:
                result.append(True)

        return all(result)
