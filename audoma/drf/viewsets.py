import random
from typing import (
    Any,
    Dict,
    List,
    Union,
)

from rest_framework import viewsets
from rest_framework.exceptions import ErrorDetail
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from audoma.drf.generics import GenericAPIView


class AudomaPagination(PageNumberPagination):
    """
    A simple page number based style that supports page numbers as
    query parameters.

    Note:
        If this won't be used it'll cause less explicit pagination documentation.
        This class does not provide any additional functionality.

    Args:
        page_size (int) - number of items per page - by default this is set to 25
        max_page_size (int) - maximum number of items per page - by default this is set to 2000
    """

    page_size = 25
    max_page_size = 2000

    def get_paginated_response_schema(self, schema: List[dict]) -> dict:
        """
        Simple method to add pagination information to the schema.

        Args:
            schema (List[dict]) - list of schema items
        Returns:
            Dictionary with pagination information including examples
        """
        return {
            "type": "object",
            "properties": {
                "count": {"type": "integer", "example": random.randint(1, 100)},
                "message": {
                    "type": "string",
                    "nullable": True,
                },
                "next": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.org/accounts/?page=4",
                },
                "previous": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.org/accounts/?page=2",
                },
                "results": schema,
            },
        }


class UnknownExceptionContentTypeError(Exception):
    ...


class GenericViewSet(viewsets.ViewSetMixin, GenericAPIView):
    pagination_class = AudomaPagination

    def _parse_single_response_data_item(self, item):
        if isinstance(item, str):
            return item
        elif isinstance(item, ErrorDetail):
            return str(item)
        elif isinstance(item, list) or isinstance(item, dict):
            return self._parse_response_data(item)
        else:
            raise UnknownExceptionContentTypeError

    def _parse_response_data(
        self, response_data: Union[List[Any], Dict[Any, Any]]
    ) -> Union[List[Any], Dict[Any, Any]]:
        parsed_data = []
        if isinstance(response_data, list):
            for item in response_data:
                parsed_data.append(self._parse_single_response_data_item(item))
        elif isinstance(response_data, dict):
            for key, item in response_data.items():
                item = self._parse_single_response_data_item(item)
                parsed_data.append((key, item))
            parsed_data = dict(parsed_data)

        return parsed_data

    def handle_exception(self, exc: Exception) -> Response:
        response = super().handle_exception(exc)
        if isinstance(response.data, dict):
            if response.status_code != 418:
                for k in response.data:
                    if isinstance(response.data[k], list):
                        if not all(isinstance(item, str) for item in response.data[k]):
                            response.data[k] = self._parse_response_data(
                                response.data[k]
                            )
                response.data = {"errors": response.data}
        elif isinstance(response.data, list):
            response.data = {"errors": response.data}
        return response
