from dataclasses import dataclass
from inspect import isclass
from typing import (
    Iterable,
    List,
    Type,
    Union,
)

from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from django.db.models import Model
from django.views import View


# TODO - fix typing
@dataclass
class OperationExtractor:

    collectors: Union[dict, BaseSerializer]
    results: Union[dict, BaseSerializer]
    errors: List[Union[APIException, Type[APIException]]]

    def extract_operation(
        self, request: Request, code: int = None, operation_category="response"
    ):
        if operation_category == "response":
            return self._extract_response_operation(request, code)
        elif operation_category == "collect":
            return self._extract_collect_operation(request)
        else:
            raise ValueError("Unknown operation_category")

    def _extract_response_operation(self, request, code):
        if code >= 400:
            error_data = self.errors.get(code, {})
            error_kwargs = {
                "status_code": code,
                "detail": error_data.get("detail"),
                "code": error_data.get("error_code"),
            }
            return self._create_exception(error_kwargs)

        if not self.results or (
            isclass(self.results) and issubclass(self.results, BaseSerializer)
        ):
            return self.results

        if isinstance(list(self.results.keys())[0], str) and request:
            method = request.method.lower()
            response = self.results.get(method)
            if code and isinstance(response, dict):
                response = response.get(code)
            return response

        elif isinstance(list(self.results.keys())[0], int) and code:
            response = self.results.get(code)
            return response

        return None

    def _create_exception(self, options):
        status_code = options.pop("status_code")
        exception = APIException(**options)
        exception.status_code = status_code if status_code else exception.status_code
        return exception

    def _extract_collect_operation(self, request):
        if not self.collectors or (
            isclass(self.collectors) and issubclass(self.collectors, BaseSerializer)
        ):
            return self.collectors

        method = request.method.lower()
        return self.collectors.get(method)


def apply_response_operation(
    operation: Union[str, APIException, BaseSerializer],
    instance: Union[Iterable, str, APIException, Model],
    code: int,
    view: View,
    many: bool,
) -> Response:

    if isinstance(operation, APIException):
        raise operation

    if isinstance(operation, str):
        instance = instance or operation
        instance = {"message": instance}
        return Response(instance, status=code)

    serializer_class = operation

    if instance:
        if isinstance(instance, Iterable) and not isinstance(instance, dict):
            serializer_kwargs = {"data": instance, "many": True}
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
