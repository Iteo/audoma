from dataclasses import dataclass
from inspect import isclass
from typing import (
    List,
    Type,
    Union,
)

from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer


@dataclass
class OperationExtractor:

    collectors: Union[dict, Type[BaseSerializer]]
    results: Union[dict, Type[BaseSerializer], str]
    errors: List[Union[APIException, Type[APIException]]]

    def _create_exception(self, options: dict) -> APIException:
        """
        Create proper exception if error status code, found defined in the response.
        Args:
            * options - kwargs for APIException instance.
        Returns: APIException instance.
        """
        status_code = options.pop("status_code")
        exception = APIException(**options)
        exception.status_code = status_code if status_code else exception.status_code
        return exception

    def _extract_response_operation(
        self, request: Request, code: int
    ) -> Union[dict, Type[BaseSerializer], str, APIException]:
        """
        Extracts response operation from the defined in audoma_action dictionary.

        Args:
            * request - request object
            * code - response status code, this should be passed as an integer.
        Returns: Serializer instance, dictionary, string or APIException.
        """
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

    def _extract_collect_operation(self, request: Request) -> Type[BaseSerializer]:
        """
        Extracts collect operation from the defined in audoma_action dictionary.

        Args:
            * request - request object
        Returns: Serializer class.
        """
        if not self.collectors or (
            isclass(self.collectors) and issubclass(self.collectors, BaseSerializer)
        ):
            return self.collectors

        method = request.method.lower()
        return self.collectors.get(method)

    def extract_operation(
        self, request: Request, code: int = None, operation_category="response"
    ) -> Union[dict, Type[BaseSerializer], str, APIException]:
        """
        Extracts proper operation from the defined in audoma_action dictionary.
        Args:
            * request - request object
            * code - response status code, this should be given only for responses.
                It should be given as an integer
            * operation_category - operation category, it can be either "response" or "collect".
                This determines if the extracted operation should be either response or request operation.
        Returns: Serializer instance, dictionary, string or APIException.
        """
        if operation_category == "response":
            return self._extract_response_operation(request, code)
        elif operation_category == "collect":
            return self._extract_collect_operation(request)
        else:
            raise ValueError("Unknown operation_category")
