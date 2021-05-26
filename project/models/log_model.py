from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils


class SystemLogModel():

    def __init__(
            self,
            message: str,
            category: str = "Error",
            business_process_id: str = "",
            process: str = None,
            class_name: str = None,
            module_name: str = None):
        if not GeneralsUtils.validate_string(message):
            raise TypeError("The 'message' is not in the correct format")

        elif not GeneralsUtils.validate_string(category):
            raise TypeError("The 'category' is not in the correct format")

        elif len([system_log_category_key
                  for system_log_category_key in
                  Constants.SYSTEM_LOG_CATEGORIES
                  if Constants.SYSTEM_LOG_CATEGORIES[
                      system_log_category_key] ==
                  category.capitalize()]) == 0:
            raise ValueError("The 'category' was not recognized")

        elif not GeneralsUtils.validate_string(business_process_id):
            raise TypeError(
                "The 'business_process_id' is not in the correct format")

        elif process is not None and\
                not GeneralsUtils.validate_string(process):
            raise TypeError("The 'process' is not in the correct format")

        elif class_name is not None and\
                not GeneralsUtils.validate_string(class_name):
            raise TypeError("The 'class_name' is not in the correct format")

        elif module_name is not None and\
                not GeneralsUtils.validate_string(module_name):
            raise TypeError("The 'module_name' is not in the correct format")

        self.message = message
        self.category = category
        self.business_process_id = business_process_id
        self.process = process
        self.class_name = class_name
        self.module_name = module_name

        self.owner =\
            GeneralsUtils.get_global_data(
                Constants.GLOBAL_DATA_OWNER_KEY)
        self.transaction_id =\
            GeneralsUtils.get_global_data(
                Constants.GLOBAL_DATA_TRANSACTION_ID_KEY)
        self.user_id =\
            GeneralsUtils.get_global_data(
                Constants.GLOBAL_DATA_USER_ID_KEY)

        self.datestamp = GeneralsUtils.get_datetime("Iso")

    message = None
    category = None
    business_process_id = None
    source = None
    class_name = None
    module_name = None
    owner = None
    transaction_id = None
    user_id = None
    datestamp = None
    process = None
