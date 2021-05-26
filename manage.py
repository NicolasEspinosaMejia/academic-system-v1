import json

from datetime import datetime

from flask import g, request
from flask_script import Manager

from project.app import create_app
from project.constants import Constants
from project.logs.system_log import SystemLog
from project.models.response_model import ResponseBodyModel
from project.resources.utils.generals_utils import GeneralsUtils


app = create_app()


@app.before_request
def before_request_function():
    with_restrictions = True
    fail = False
    request_verb = "UNKNOWN"
    g.dateTimeStart = datetime.utcnow()
    g.endpoint = request.endpoint
    g.response_body = ResponseBodyModel(
        method=g.endpoint,
        status_code=200)

    if hasattr(request, "method") and\
       GeneralsUtils.validate_string(request.method):
        request_verb = request.method.upper()

    if any(excluded_request_path in request.base_url
       for excluded_request_path in Constants.EXCLUDED_REQUEST_PATHS) or\
       any(excluded_request_verb in request_verb
       for excluded_request_verb in Constants.EXCLUDED_REQUEST_VERBS):
        with_restrictions = False

    g.with_restrictions = with_restrictions

    if with_restrictions:
        for request_header_attribute in Constants.REQUEST_HEADERS_ATTRIBUTES:
            request_header_attribute_name = request_header_attribute["NAME"]
            request_header_value = request.headers.\
                get(request_header_attribute_name)

            if request_header_attribute["REQUIRED"] and\
               request_header_value is None:
                fail = True
                continue

            GeneralsUtils.set_global_data(
                request_header_attribute["GLOBAL_DATA_KEY"],
                request_header_value)

        g.response_body.transaction_id = GeneralsUtils.get_global_data(
            Constants.GLOBAL_DATA_TRANSACTION_ID_KEY)

        if fail:
            g.response_body.set_status_code(403)
            g.response_body.add_detail(
                message="A required parameter " +
                        "was not sent to continue the operation",
                level="Error")
            return g.response_body.to_dict()


@app.after_request
def after_request_function(response):
    fail = None
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.method = g.endpoint

    response_body = g.response_body

    if response.status_code == 404:
        response_body.set_status_code(404)
        response_body.add_detail(
            message="Requested method not found",
            level="Error")
        fail = True

    if not g.with_restrictions:
        return response

    if not fail:
        try:
            response_data = None
            if response.is_json:
                response_data = json.loads(response.get_data())

            response_body_status_code_key =\
                Constants.RESPONSE_BODY_STATUS_CODE_KEY
            if response_body_status_code_key in response_data:
                response_body.set_status_code(
                    response_data[response_body_status_code_key])

            response_body.set_data(response_data)

        except Exception as error:
            message = "Error getting the response data"
            SystemLog.add(
                message=message,
                error=error,
                process="Initial setup")
            response_body.set_status_code(500)
            response_body.add_detail(
                message=message,
                level="Error")

    response.status_code = response_body.status_code
    response.set_data(json.dumps(response_body.to_dict()))

    return response


manager = Manager(app)

if __name__ == "__main__":
    manager.run()
