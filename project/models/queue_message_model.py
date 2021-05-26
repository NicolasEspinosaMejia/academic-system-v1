from project.constants import Constants
from project.resources.utils.generals_utils import GeneralsUtils


class QueueMessageModel():

    def __init__(self, target, event_type, data):
        log_message_process_value =\
            Constants.QUEUE_MESSAGE_PROCESS_VALUE
        global_data_owner_data_key =\
            Constants.GLOBAL_DATA_OWNER_KEY
        global_data_user_id_key =\
            Constants.GLOBAL_DATA_USER_ID_KEY
        global_data_transaction_id_key =\
            Constants.GLOBAL_DATA_TRANSACTION_ID_KEY

        if not isinstance(data, list):
            data = [data]

        self.target = target
        self.eventType = event_type
        self.data = data
        self.source = Constants.QUEUE_MESSAGE_SOURCE_VALUE
        self.owner =\
            GeneralsUtils.get_global_data(global_data_owner_data_key)
        self.transactionId = GeneralsUtils.\
            get_global_data(global_data_transaction_id_key)
        self.userId =\
            GeneralsUtils.get_global_data(global_data_user_id_key)
        self.datestamp = GeneralsUtils.get_datetime("Iso")
        self.process = log_message_process_value

    target = None
    eventType = None
    data = None
    source = None
    owner = None
    transactionId = None
    userId = None
    datestamp = None
    process = None

    def to_dict(self):
        return GeneralsUtils.instance_to_dict(self)
