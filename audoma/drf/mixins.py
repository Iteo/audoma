"""
This module overwrites basic mixins provided bu django rest framework.
Mixins defined here should be used instead of default drf's mixins.
Those mixins should be used to allow usage of extended `get_serializer` method>

Example:

    from audoma.drf import mixins
    from audoma.drf import viewsets

    class ExampleModelViewSet(
        mixins.ActionModelMixin,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet,
    ):
        serializer_class = ExampleModelSerializer
        queryset = ExampleModel.objects.all()

"""

from typing import (
    Any,
    Dict,
    List,
)

from rest_framework import (
    mixins,
    serializers,
    status,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.settings import api_settings

from django.core.exceptions import ValidationError


class ActionModelMixin:
    def perform_action(
        self,
        request: Request,
        success_status: int = status.HTTP_200_OK,
        instance: Any = None,
        partial: bool = False,
        **kwargs
    ) -> Response:
        if instance:
            serializer = self.get_serializer(
                data=request.data, instance=instance, partial=partial
            )
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return_serializer = self.get_result_serializer(serializer.instance)
        headers = self.get_success_headers(return_serializer.data)

        return Response(return_serializer.data, status=success_status, headers=headers)

    def retrieve_instance(
        self,
        request: Request,
        instance: Any = None,
        success_status: int = status.HTTP_200_OK,
        **kwargs
    ) -> Response:
        if instance is None:
            instance = self.get_object()
        assert instance is not None
        serializer = self.get_result_serializer(instance)
        return Response(serializer.data, status=success_status)

    def get_success_headers(self, data: dict) -> dict:
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class CreateModelMixin(mixins.CreateModelMixin):
    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return_serializer = self.get_result_serializer(serializer.instance)
        headers = self.get_success_headers(return_serializer.data)
        return Response(
            return_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class ListModelMixin(mixins.ListModelMixin):
    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_result_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_result_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_paginated_response(self, data: List[Dict]) -> Response:
        ret = super().get_paginated_response(data)
        if hasattr(self, "get_list_message"):
            assert callable(self.get_list_message)
            ret.data["message"] = self.get_list_message()
        else:
            ret.data["message"] = None
        return ret


class RetrieveModelMixin(mixins.RetrieveModelMixin):
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_result_serializer(instance)
        return Response(serializer.data)


class UpdateModelMixin(mixins.UpdateModelMixin):
    def update(self, request: Request, *args, **kwargs) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return_serializer = self.get_result_serializer(serializer.instance)
        return Response(return_serializer.data)


class DestroyModelMixin(mixins.DestroyModelMixin):
    def destroy(self, request: Request, *args, **kwargs) -> Response:

        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ValidationError as e:
            raise serializers.ValidationError({"detail": e.message})
        return Response(status=status.HTTP_204_NO_CONTENT)


class BulkCreateModelMixin(CreateModelMixin):
    """
    Either create a single or many model instances in bulk by using the
    Serializers ``many=True`` ability from Django REST >= 2.2.5.
    .. note::
        This mixin uses the same method to create model instances
        as ``CreateModelMixin`` because both non-bulk and bulk
        requests will use ``POST`` request method.
    """

    def create(self, request: Request, *args, **kwargs) -> Response:
        bulk = isinstance(request.data, list)
        if not bulk:
            return super(BulkCreateModelMixin, self).create(request, *args, **kwargs)
        else:
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_bulk_create(serializer)
            serializer = self.get_result_serializer(serializer.instance, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer: BaseSerializer) -> None:
        self.perform_create(serializer)


class BulkUpdateModelMixin(object):
    """
    Update model instances in bulk by using the Serializers
    ``many=True`` ability from Django REST >= 2.2.5.
    """

    def get_object(self) -> Any:
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg in self.kwargs:
            return super().get_object()
        # If the lookup_url_kwarg is not present
        # get_object() is most likely called as part of options()
        # which by default simply checks for object permissions
        # and raises permission denied if necessary.
        # Here we don't need to check for general permissions
        # and can simply return None since general permissions
        # are checked in initial() which always gets executed
        # before any of the API actions (e.g. create, update, etc)
        return

    def bulk_update(self, request: Request, *args, **kwargs) -> Response:
        partial = kwargs.pop("partial", False)
        # restrict the update to the filtered queryset
        serializer = self.get_serializer(
            self.filter_queryset(self.get_queryset()),
            data=request.data,
            many=True,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_bulk_update(self, request: Request, *args, **kwargs) -> Response:
        kwargs["partial"] = True
        return self.bulk_update(request, *args, **kwargs)

    def perform_update(self, serializer: BaseSerializer) -> None:
        serializer.save()

    def perform_bulk_update(self, serializer: BaseSerializer) -> None:
        self.perform_update(serializer)


# class BulkDestroyModelMixin(object):
#     """
#     Destroy model instances.
#     """

#     def allow_bulk_destroy(self, qs: Any, filtered: Any) -> bool:
#         """
#         Hook to ensure that the bulk destroy should be allowed.
#         By default this checks that the destroy is only applied to
#         filtered querysets.
#         """
#         return qs is not filtered
#     def bulk_destroy(self, request: Request, *args, **kwargs) -> Response:
#         qs = self.get_queryset()
#         filtered = self.filter_queryset(qs)
#         if not self.allow_bulk_destroy(qs, filtered):
#             return Response(status=status.HTTP_400_BAD_REQUEST)

#         self.perform_bulk_destroy(filtered)
#         return Response(status=status.HTTP_204_NO_CONTENT)
#     def perform_destroy(self, instance: object) -> None:
#         instance.delete()

#     def perform_bulk_destroy(self, objects: Any) -> None:
#         for obj in objects:
#             self.perform_destroy(obj)
