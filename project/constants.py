

class Constants():

    CONFIG_APP_VERSION_KEY = "APP_VERSION"
    CONFIG_CONNECTION_STRINGS_KEY = "CONNECTION_STRINGS"
    CONFIG_DATABASE_CACHE_KEYS_KEY = "DATABASE_CACHE_KEYS"
    CONFIG_DEBUG_KEY = "DEBUG"

    GLOBAL_DATA_HES_KEY = "hes"
    GLOBAL_DATA_OWNER_KEY = "owner"
    GLOBAL_DATA_USER_ID_KEY = "user_id"
    GLOBAL_DATA_TRANSACTION_ID_KEY = "transaction_id"

    BODY_NODE_OWNER_KEY = "owner"
    BODY_NODE_OWNER_OWNER_KEY = "owner"
    BODY_PACKAGE_OWNER_ATTRIBUTES = (
        {
            "NAME": BODY_NODE_OWNER_OWNER_KEY,
            "GLOBAL_DATA_KEY": GLOBAL_DATA_OWNER_KEY,
            "REQUIRED": True
        })

    DATE_TIME_FORMATS = ("%Y-%m-%dT%H:%M:%S.%f%Z",)

    ELASTIC_CACHE_CLIENT_NAME = "elasticache"

    EXCLUDED_REQUEST_PATHS = ("swagger",)
    EXCLUDED_REQUEST_VERBS = ("OPTIONS",)

    EXTERNAL_SYSTEM_KEY = "externalSystem"
    EXTERNAL_SYSTEM_NAME_KEY = "name"
    EXTERNAL_SYSTEM_CONNECTION_NAME_KEY = "connectionName"
    EXTERNAL_SYSTEM_HOST_KEY = "host"
    EXTERNAL_SYSTEM_LANGUAGE_KEY = "language"
    EXTERNAL_SYSTEM_OWNER_KEY = "owner"
    EXTERNAL_SYSTEM_VERSION_KEY = "version"
    EXTERNAL_SYSTEM_ATTRIBUTES = (
        {
            "NAME": EXTERNAL_SYSTEM_CONNECTION_NAME_KEY,
            "REQUIRED": True
        },
        {
            "NAME": EXTERNAL_SYSTEM_HOST_KEY,
            "REQUIRED": True
        },
        {
            "NAME": EXTERNAL_SYSTEM_LANGUAGE_KEY,
            "REQUIRED": True
        },
        {
            "NAME": EXTERNAL_SYSTEM_NAME_KEY,
            "REQUIRED": True
        },
        {
            "NAME": EXTERNAL_SYSTEM_OWNER_KEY,
            "REQUIRED": False
        }
    )

    LANGUAGE_MULTI_SPEAK_ID = "MSP"
    LANGUAGE_PRIME_ANALYTICS_PLUS_ID = "PAP"

    TYPE_REFERENCE_PRIME_ANALYTICS_PLUS = "1.0.0"

    QUEUE_MESSAGE_DATA_KEY = "data"
    QUEUE_MESSAGE_EVENT_TYPES = {
        "MSP": {
            "5.0.0": {
                "CONTROL_ACTION_CONNECT":
                    "MSP-COM-controlAction.cnt",
                "CONTROL_ACTION_DISCONNECT":
                    "MSP-COM-controlAction.dct",
                "EVENT_SUBSCRIBE":
                    "MSP-COM-event.sub",
                "EVENT_GET_END_DEVICE_EVENTS":
                    "MSP-COM-event.odm",
                "EXTERNAL_SYSTEM_CHECK_STATE":
                    "MSP-COM-externalSystem.cks",
                "EXTERNAL_SYSTEM_GET_CAPABILITIES":
                    "MSP-COM-externalSystem.gcp",
                "EXTERNAL_SYSTEM_GET_SUBSCRIPTION_CAPABILITIES":
                    "MSP-COM-externalSystem.gsc",
                "EXTERNAL_SYSTEM_GET_IDENTIFIER":
                    "MSP-COM-externalSystem.gei",
                "METERING_SYSTEM_DISCOVER":
                    "MSP-COM-topology.dsc",
                "READING_GET_ON_DEMAND":
                    "MSP-COM-reading.odm",
                "SCHEDULE_CREATE_READING":
                    "MSP-COM-schedule.cre",
                "SCHEDULE_ENABLE_READING":
                    "MSP-COM-schedule.ere"
            }
        },
        "PAP": {
            "1.0.0": {
                "READING_GET_ON_DEMAND": "PAP-PRM-readingOnDemand.ntf",
                "CONTROL_ACTION_EXECUTE": "PAP-PRM-controlAction.ntf",
                "METERING_SYSTEM_DISCOVER": "PAP-PRM-topology.ntf"
            }
        }
    }
    QUEUE_MESSAGE_EVENT_TYPE_KEY = "eventType"
    QUEUE_MESSAGE_EVENT_TYPE_ACTION_KEY =\
        "queue_message_event_type_action"
    QUEUE_MESSAGE_EVENT_TYPE_ENTITY_KEY =\
        "queue_message_event_type_entity"
    QUEUE_MESSAGE_EVENT_TYPE_LANGUAGE_KEY =\
        "queue_message_event_type_language"
    QUEUE_MESSAGE_EVENT_TYPE_TYPE_KEY =\
        "queue_message_event_type_type"
    QUEUE_MESSAGE_OWNER_KEY = "owner"
    QUEUE_MESSAGE_TRANSACTION_ID_KEY = "transactionId"
    QUEUE_MESSAGE_USER_ID_KEY = "userId"
    QUEUE_MESSAGE_ATTRIBUTES = (
        {
            "NAME": QUEUE_MESSAGE_OWNER_KEY,
            "GLOBAL_DATA_KEY": GLOBAL_DATA_OWNER_KEY,
            "REQUIRED": True
        },
        {
            "NAME": QUEUE_MESSAGE_TRANSACTION_ID_KEY,
            "GLOBAL_DATA_KEY": GLOBAL_DATA_TRANSACTION_ID_KEY,
            "REQUIRED": True
        },
        {
            "NAME": QUEUE_MESSAGE_USER_ID_KEY,
            "GLOBAL_DATA_KEY": GLOBAL_DATA_USER_ID_KEY,
            "REQUIRED": True
        })
    QUEUE_MESSAGE_PROCESS_VALUE = "ExecuteCommands"
    QUEUE_MESSAGE_SOURCE_VALUE = "Interoperability"

    READ_FILE_OUTPUT_TYPES = ("json", "yaml")

    REQUEST_BODY_EXTERNAL_SYSTEM_NAME_KEY = "externalSystemName"
    REQUEST_BODY_EXTERNAL_SYSTEM_NAMES_KEY = "externalSystemNames"
    REQUEST_BODY_EXTERNAL_SYSTEM_CONNECTION_NAME_KEY = "connectionName"
    REQUEST_BODY_EXTERNAL_SYSTEMS_KEY = "externalSystems"
    REQUEST_BODY_READING_TYPE_CODE_KEY = "readingTypeCode"
    REQUEST_BODY_READING_TYPE_CODES_KEY = "readingTypeCodes"
    REQUEST_BODY_SCHEDULE_ID_KEY = "scheduleId"
    REQUEST_BODY_SCHEDULE_GUID_KEY = "scheduleGuid"
    REQUEST_BODY_VARIABLE_ID_KEY = "variableId"

    REQUEST_HEADER_OWNER_KEY = "Owner"
    REQUEST_HEADER_USER_ID_KEY = "User-Id"
    REQUEST_HEADER_TRANSACTION_ID_KEY = "Transaction-Id"
    REQUEST_HEADERS_ATTRIBUTES = (
        {
            "NAME": REQUEST_HEADER_OWNER_KEY,
            "GLOBAL_DATA_KEY": GLOBAL_DATA_OWNER_KEY,
            "REQUIRED": True
        },
        {
            "NAME": REQUEST_HEADER_TRANSACTION_ID_KEY,
            "GLOBAL_DATA_KEY": GLOBAL_DATA_TRANSACTION_ID_KEY,
            "REQUIRED": True
        },
        {
            "NAME": REQUEST_HEADER_USER_ID_KEY,
            "GLOBAL_DATA_KEY": GLOBAL_DATA_USER_ID_KEY,
            "REQUIRED": True
        })

    RESPONSE_BODY_API_VERSION_KEY = "apiVersion"
    RESPONSE_BODY_DATA_KEY = "data"
    RESPONSE_BODY_DETAIL_LEVELS_ENUM = ("Error", "Information", "Warning")
    RESPONSE_BODY_DETAILS_KEY = "details"
    RESPONSE_BODY_DETAILS_LEVEL_KEY = "level"
    RESPONSE_BODY_DETAILS_MESSAGE_KEY = "message"
    RESPONSE_BODY_DETAILS_VALUES_KEY = "values"
    RESPONSE_BODY_METHOD_KEY = "method"
    RESPONSE_BODY_RESULT_KEY = "result"
    RESPONSE_BODY_STATUS_CODE_KEY = "statusCode"
    RESPONSE_BODY_TRANSACTION_ID_KEY = "transactionId"
    RESPONSE_BODY_VARIABLE_ID_KEY = "variableId"

    SQS_MESSAGE_MESSAGE_PROPERTY_NAME = "message_id"
    SQS_RESOURCE_NAME = "sqs"

    SYSTEM_LOG_CATEGORY_DEBUG = "Debug"
    SYSTEM_LOG_CATEGORY_ERROR = "Error"
    SYSTEM_LOG_CATEGORY_INFORMATION = "Information"
    SYSTEM_LOG_CATEGORY_WARNING = "Warning"
    SYSTEM_LOG_CATEGORIES = {
        "DEBUG": SYSTEM_LOG_CATEGORY_DEBUG,
        "ERROR": SYSTEM_LOG_CATEGORY_ERROR,
        "INFORMATION": SYSTEM_LOG_CATEGORY_INFORMATION,
        "WARNING": SYSTEM_LOG_CATEGORY_WARNING}
