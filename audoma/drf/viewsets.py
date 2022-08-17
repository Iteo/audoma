import json
import random
from typing import (
    Any,
    List,
)

from rest_framework import viewsets
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


class GenericViewSet(viewsets.ViewSetMixin, GenericAPIView):
    pagination_class = AudomaPagination

    def _parse_response_data(self, response_data: List[Any]) -> List[str]:
        parsed_data = []
        for item in response_data:
            if isinstance(item, str):
                parsed_data.append(item)
            else:
                parsed_data.append(json.dumps(item))
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
                        response.data[k] = " ".join(response.data[k])
                response.data = {"errors": response.data}
        return response
