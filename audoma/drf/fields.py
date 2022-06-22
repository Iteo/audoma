"""
This module is an override for default drf's field module.
Most of those fields, are providing additional example functionality,
and also has defined schema type.
"""

import sys

import exrex
import phonenumbers
from djmoney.contrib.django_rest_framework import MoneyField
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
    "SerializerMethodField",
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
