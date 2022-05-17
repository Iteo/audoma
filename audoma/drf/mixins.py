import random
from typing import (
    Any,
    Dict,
    List,
)

import exrex
from drf_spectacular.drainage import set_override
from rest_framework import (
    mixins,
    status,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings

from django.core import validators


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
        from rest_framework import serializers

        from django.core.exceptions import ValidationError

        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ValidationError as e:
            raise serializers.ValidationError({"detail": e.message})
        return Response(status=status.HTTP_204_NO_CONTENT)


class DEFAULT:
    pass


class Example:
    def __init__(self, field, example=DEFAULT):
        self.field = field
        self.example = example

    def generate_value(self):
        return DEFAULT

    def get_value(self):
        if self.example is not DEFAULT:
            if callable(self.example):
                return self.example()
            return self.example
        return self.generate_value()

    def to_representation(self, value):
        return self.field.to_representation(value)


class NumericExample(Example):
    def generate_value(self):
        min_val = getattr(self.field, "min_value", 1) or 1
        max_val = getattr(self.field, "max_value", 1000) or 1000
        return random.uniform(min_val, max_val)


class RegexExample(Example):
    def generate_value(self):
        regex_validators = [
            validator
            for validator in self.field.validators
            if isinstance(validator, validators.RegexValidator)
        ]
        if regex_validators:
            regex_validator = regex_validators[0]
            return exrex.getone(regex_validator.regex.pattern)
        return None


class ExampleMixin:
    audoma_example_class = Example

    def __init__(self, *args, example=DEFAULT, **kwargs) -> None:
        self.audoma_example = self.audoma_example_class(self, example)
        super().__init__(*args, **kwargs)
        example = self.audoma_example.get_value()
        if example is not DEFAULT:
            has_annotation = (
                hasattr(self, "_spectacular_annotation")
                and "field" in self._spectacular_annotation
                and isinstance(self._spectacular_annotation["field"], dict)
            )
            example_representation = self.audoma_example.to_representation(example)
            field = {"example": example_representation}
            if has_annotation:
                field = self._spectacular_annotation["field"].copy()
                field["example"] = example_representation

            set_override(
                self,
                "field",
                field,
            )


class NumericExampleMixin(ExampleMixin):
    audoma_example_class = NumericExample


class RegexExampleMixin(ExampleMixin):
    audoma_example_class = RegexExample


class BulkCreateModelMixin(CreateModelMixin):
    """
    Either create a single or many model instances in bulk by using the
    Serializers ``many=True`` ability from Django REST >= 2.2.5.
    .. note::
        This mixin uses the same method to create model instances
        as ``CreateModelMixin`` because both non-bulk and bulk
        requests will use ``POST`` request method.
    """

    def create(self, request, *args, **kwargs):
        bulk = isinstance(request.data, list)
        if not bulk:
            return super(BulkCreateModelMixin, self).create(request, *args, **kwargs)

        else:
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_bulk_create(serializer)
            serializer = self.get_result_serializer(serializer.instance, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        return self.perform_create(serializer)


class BulkUpdateModelMixin(object):
    """
    Update model instances in bulk by using the Serializers
    ``many=True`` ability from Django REST >= 2.2.5.
    """

    def get_object(self):
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

    def bulk_update(self, request, *args, **kwargs):
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

    def partial_bulk_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.bulk_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save()

    def perform_bulk_update(self, serializer):
        return self.perform_update(serializer)


class BulkDestroyModelMixin(object):
    """
    Destroy model instances.
    """

    def allow_bulk_destroy(self, qs, filtered):
        """
        Hook to ensure that the bulk destroy should be allowed.
        By default this checks that the destroy is only applied to
        filtered querysets.
        """
        return qs is not filtered

    def bulk_destroy(self, request, *args, **kwargs):
        qs = self.get_queryset()

        filtered = self.filter_queryset(qs)
        if not self.allow_bulk_destroy(qs, filtered):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        self.perform_bulk_destroy(filtered)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def perform_bulk_destroy(self, objects):
        for obj in objects:
            self.perform_destroy(obj)
