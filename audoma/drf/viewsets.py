from rest_framework import viewsets
from split.helpers import V2Pagination
from v2_api.generics import GenericAPIView


class GenericViewSet(viewsets.ViewSetMixin, GenericAPIView):
    pagination_class = V2Pagination

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if isinstance(response.data, dict):
            if response.status_code != 418:
                for k in response.data:
                    if isinstance(response.data[k], list):
                        response.data[k] = " ".join(response.data[k])
                response.data = {"errors": response.data}
        return response
