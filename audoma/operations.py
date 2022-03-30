from inspect import isclass

from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from django.db.models import QuerySet


class OperationExtractor:
    def __init__(self, collectors, responses, errors):
        self.collectors = collectors
        self.responses = responses
        self.errors = errors

    def extract_operation(self, request, code=None, operation_category="response"):
        if operation_category == "response":
            return self.__extract_response_operation(request, code)
        elif operation_category == "collect":
            return self.__extract_collect_operation(request)
        else:
            raise ValueError("Unknown operation_category")

    def __extract_response_operation(self, request, code):
        if code >= 400:
            error_data = self.errors.get(code, {})
            error_kwargs = {
                "status_code": code,
                "detail": error_data.get("detail"),
                "code": error_data.get("error_code"),
            }
            return self.__create_exception(error_kwargs)

        if not self.responses or (
            isclass(self.responses) and issubclass(self.responses, BaseSerializer)
        ):
            return self.responses

        if isinstance(list(self.responses.keys())[0], str) and request:
            method = request.method.lower()
            response = self.responses.get(method)
            if code and isinstance(response, dict):
                response = response.get(code)
            return response

        elif isinstance(list(self.responses.keys())[0], int) and code:
            response = self.responses.get(code)
            return response

        return None

    def __create_exception(self, options):
        status_code = options.pop("status_code")
        exception = APIException(**options)
        exception.status_code = status_code if status_code else exception.status_code
        return exception

    def __extract_collect_operation(self, request):
        if not self.collectors or (
            isclass(self.collectors) and issubclass(self.collectors, BaseSerializer)
        ):
            return self.collectors

        method = request.method.lower()
        return self.collectors.get(method)


def apply_response_operation(operation, instance, code, view, many):

    if isinstance(operation, APIException):
        raise operation

    if isinstance(operation, str):
        instance = instance or operation
        instance = {"message": instance}
        return Response(instance, status=code)

    serializer_class = operation

    if instance:
        if isinstance(instance, QuerySet):
            serializer_kwargs = {"data": instance, "many": many}
        else:
            serializer_kwargs = {"instance": instance, "many": False}
    else:
        serializer_kwargs = {"many": many}
    return_serializer = (
        serializer_class(**serializer_kwargs)
        if serializer_class
        else view.get_result_serializer(**serializer_kwargs)
    )
    headers = view.get_success_headers(return_serializer.data)

    return Response(return_serializer.data, status=code, headers=headers)
