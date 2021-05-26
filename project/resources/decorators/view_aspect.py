import connexion

from flask import g

from project.logs.system_log import SystemLog
from project.resources.utils.generals_utils import GeneralsUtils


class ViewAspect(object):

    def __init__(self, method):
        self.method = method

    def __call__(self, *args):
        result = []
        response_body = g.response_body
        fail = None

        try:
            method_kwargs = {
                "data": GeneralsUtils.get_request_data(connexion.request)}

            request_args = connexion.request.args
            for arg_name in request_args:
                method_kwargs[arg_name] = request_args[arg_name]

            method_kwargs = GeneralsUtils.clean_dictionary(method_kwargs)
            fail = False

        except Exception as error:
            message = "Error getting request data"
            SystemLog.add(
                message=message,
                error=error,
                process="Getting initial data or parameters")
            response_body.add_detail(message=message, level="Error")
            fail = True

        if not fail:
            try:
                result = self.method(**method_kwargs)
                fail = False

            except Exception as error:
                message = "An error occurred during the " +\
                    "execution of the operation"
                SystemLog.add(
                    message=message,
                    error=error,
                    process="Processing request")
                response_body.add_detail(message=message, level="Error")
                fail = True

        if not fail:
            response_body.data = GeneralsUtils.format_response_data(result)

        if fail is True:
            response_body.set_status_code(500)

        return response_body.to_dict()
