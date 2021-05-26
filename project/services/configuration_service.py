from project.services.service import Service


class ConfigurationService(Service):

    def check_state(self, component: str = None) -> dict:
        result = {}

        component = component or ""
        if not isinstance(component, str):
            component = ""

        component = component.upper()

        if component == "API" or component == "":
            result["API"] = True

        if component == "REDIS" or component == "":
            result["Redis"] = True

        if component == "SQS" or component == "":
            result["SQS"] = True

        return result
