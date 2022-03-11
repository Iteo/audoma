from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from audoma.drf.generics import GenericAPIView


class AudomaPagination(PageNumberPagination):
    page_size = 25
    max_page_size = 2000

    def get_paginated_response_schema(self, schema):
        return schema


class GenericViewSet(viewsets.ViewSetMixin, GenericAPIView):
    pagination_class = AudomaPagination

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if isinstance(response.data, dict):
            if response.status_code != 418:
                for k in response.data:
                    if isinstance(response.data[k], list):
                        response.data[k] = " ".join(response.data[k])
                response.data = {"errors": response.data}
        return response
