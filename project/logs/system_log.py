

from project.resources.utils.generals_utils import GeneralsUtils
from project.constants import Constants
from project.configuration_manager import ConfigurationManager
from project.models.log_model import SystemLogModel


class SystemLog:

    reports: list = []

    @staticmethod
    def add(message: str,
            error: Exception = None,
            category: str = None,
            business_process_id: str = None,
            process: str = None,
            class_name: str = None,
            module_name: str = None):
        try:
            if isinstance(message, str) and error is not None:
                message = f"{message}: {SystemLog.get_error_message(error)}"

            category = category\
                if GeneralsUtils.validate_string(category)\
                else "Error"

            business_process_id = business_process_id\
                if GeneralsUtils.validate_string(business_process_id)\
                else GeneralsUtils.get_global_data(
                    Constants.GLOBAL_DATA_TRANSACTION_ID_KEY)

            system_log_model = SystemLogModel(
                message,
                category,
                business_process_id,
                process,
                class_name,
                module_name)

            SystemLog.reports.append(system_log_model)

            if ConfigurationManager.get_config(Constants.CONFIG_DEBUG_KEY):
                print(
                    f"----------------------------------------------------\n" +
                    f"Log from 'SystemLog':\n" +
                    f"   -> Message: {system_log_model.message}\n" +
                    f"   -> Process: {system_log_model.process}\n" +
                    f"   -> Business process id: " +
                    f"{system_log_model.business_process_id}\n" +
                    f"   -> Category: {system_log_model.category}\n" +
                    f"   -> Time: {system_log_model.datestamp}\n" +
                    f"----------------------------------------------------\n")

        except RuntimeError as error:
            print(f"Error adding a log: {str(error)}")

    @staticmethod
    def get_error_message(error):
        result = ""
        if not hasattr(error, "args") or len(error.args) == 0:
            return result

        for error_arg in error.args:
            if isinstance(error_arg, str):
                result = result + error_arg

        return result
