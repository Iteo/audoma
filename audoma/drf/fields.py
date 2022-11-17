"""
This module is an override for default drf's field module.
Most of those fields, are providing additional example functionality,
and also has defined schema type.
"""

import sys
from inspect import isclass

import exrex
import phonenumbers
from djmoney.contrib.django_rest_framework import MoneyField
from drf_spectacular.drainage import set_override
from drf_spectacular.plumbing import force_instance
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from phonenumber_field import serializerfields
from phonenumber_field.phonenumber import to_python
from rest_framework import fields
from rest_framework.fields import *  # noqa: F403, F401

from django.core import validators

from audoma.example_generators import generate_lorem_ipsum
from audoma.mixins import (
    ExampleMixin,
    NumericExampleMixin,
    RegexExampleMixin,
)


field_names = [
    "BooleanField",
    "NullBooleanField",
    "EmailField",
    "SlugField",
    "URLField",
    "DateTimeField",
    "DurationField",
    "ChoiceField",
    "MultipleChoiceField",
    "FilePathField",
    "FileField",
    "ImageField",
    "ListField",
    "DictField",
    "HStoreField",
    "JSONField",
    "ReadOnlyField",
]


this = sys.modules[__name__]


for field_name in field_names:

    setattr(
        this,
        field_name,
        type(field_name, (ExampleMixin, getattr(fields, field_name)), {}),
    )


class DecimalField(NumericExampleMixin, fields.DecimalField):
    pass


@extend_schema_field(OpenApiTypes.UUID)
class UUIDField(ExampleMixin, fields.UUIDField):
    pass


class IntegerField(NumericExampleMixin, fields.IntegerField):
    pass


class FloatField(NumericExampleMixin, fields.FloatField):
    pass


class RegexField(RegexExampleMixin, fields.RegexField):
    pass


class MACAddressField(RegexExampleMixin, fields.CharField):
    def __init__(self, **kwargs) -> None:
        self.regex = "^([0-9A-F]{2}:){5}([0-9A-F]{2})|([0-9A-F]{2}-){5}([0-9A-F]{2})$"
        self.validators = [validators.RegexValidator(self.regex)]
        super().__init__(**kwargs)


@extend_schema_field(OpenApiTypes.DATE)
class DateField(ExampleMixin, fields.DateField):
    pass


@extend_schema_field(OpenApiTypes.TIME)
class TimeField(ExampleMixin, fields.TimeField):
    pass


@extend_schema_field(
    field={
        "format": "ip-address",
        "example": str(
            exrex.getone(
                r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
            )
        ),
    }
)
class IPAddressField(ExampleMixin, fields.IPAddressField):
    pass


@extend_schema_field(field={"format": "tel"})
class PhoneNumberField(ExampleMixin, serializerfields.PhoneNumberField):
    def __init__(self, *args, **kwargs) -> None:
        example = kwargs.pop("example", None)
        if example is None:
            number = phonenumbers.example_number(None)
            example = str(to_python(number))
        super().__init__(*args, example=example, **kwargs)


class CharField(ExampleMixin, fields.CharField):
    def __init__(self, *args, **kwargs) -> None:
        example = kwargs.pop("example", None)
        min_length = kwargs.get("min_length", 20)
        max_length = kwargs.get("max_length", 80)
        if not example:
            example = generate_lorem_ipsum(min_length=min_length, max_length=max_length)

        super().__init__(*args, example=example, **kwargs)


class MoneyField(NumericExampleMixin, MoneyField):
    pass


class ChoiceField(ExampleMixin, fields.ChoiceField):
    def __init__(self, choices, **kwargs):
        if isinstance(choices, dict):
            self.original_choices = list(choices.items())
        else:
            self.original_choices = choices
        super().__init__(choices, **kwargs)


class SerializerMethodField(ExampleMixin, fields.Field):
    def _parse_field(self, field):
        if field is None:
            return None
        elif isclass(field) and issubclass(field, fields.Field):
            return force_instance(field)
        elif isinstance(field, fields.Field):
            return field
        else:
            raise ValueError(
                f"Incorrect type of field, field \
                    must be an instance or a subclass of rest_framework.fields.Field.\
                        Passed value: {field}"
            )

    def __init__(self, *args, **kwargs) -> None:
        self.method_name = kwargs.pop("method_name", None)
        self.field = self._parse_field(kwargs.pop("field", None))
        self.is_writable = kwargs.pop("is_writable", False)
        if self.is_writable and self.field is None:
            raise ValueError("Writable SerializerMethodField must have field defined.")

        kwargs["source"] = "*"
        kwargs["read_only"] = not self.is_writable
        super().__init__(*args, **kwargs)

    def bind(self, field_name, parent):
        # The method name defaults to `get_{field_name}`.
        if self.method_name is None:
            self.method_name = "get_{field_name}".format(field_name=field_name)
        super().bind(field_name, parent)
        if self.field is not None:
            set_override(self, "field", self.field)

    def to_representation(self, value):
        method = getattr(self.parent, self.method_name)
        value = method(value)
        if not self.field:
            return value
        else:
            return self.field.to_representation(value)

    def get_default(self):
        default = super().get_default()
        return default

    def to_internal_value(self, data):
        if not self.is_writable:
            raise fields.SkipField
        return self.field.to_internal_value(data)

    def run_validation(self, data):
        if not self.is_writable:
            raise fields.SkipField
        return self.field.run_validation(data)
