import random

import exrex
from drf_spectacular.drainage import set_override
from rest_framework import (
    mixins,
    status,
)
from rest_framework.response import Response
from rest_framework.settings import api_settings

from django.core import validators


class ActionModelMixin:
    def perform_action(
        self,
        request,
        success_status=status.HTTP_200_OK,
        instance=None,
        partial=False,
        **kwargs
    ):
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
        self, request, instance=None, success_status=status.HTTP_200_OK, **kwargs
    ):
        if instance is None:
            instance = self.get_object()
        assert instance is not None
        serializer = self.get_result_serializer(instance)
        return Response(serializer.data, status=success_status)

    def get_success_headers(self, data):
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class CreateModelMixin(mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return_serializer = self.get_result_serializer(serializer.instance)
        headers = self.get_success_headers(return_serializer.data)
        return Response(
            return_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class ListModelMixin(mixins.ListModelMixin):
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_result_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_result_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_paginated_response(self, data):
        ret = super().get_paginated_response(data)
        if hasattr(self, "get_list_message"):
            assert callable(self.get_list_message)
            ret.data["message"] = self.get_list_message()
        else:
            ret.data["message"] = None
        return ret


class RetrieveModelMixin(mixins.RetrieveModelMixin):
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_result_serializer(instance)
        return Response(serializer.data)


class UpdateModelMixin(mixins.UpdateModelMixin):
    def update(self, request, *args, **kwargs):
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
    def destroy(self, request, *args, **kwargs):
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

    def __init__(self, *args, example=DEFAULT, **kwargs):
        self.audoma_example = self.audoma_example_class(self, example)
        super().__init__(*args, **kwargs)
        example = self.audoma_example.get_value()
        if example is not DEFAULT:
            set_override(
                self,
                "field",
                {"example": self.audoma_example.to_representation(example)},
            )


class NumericExampleMixin(ExampleMixin):
    audoma_example_class = NumericExample


class RegexExampleMixin(ExampleMixin):
    audoma_example_class = RegexExample
