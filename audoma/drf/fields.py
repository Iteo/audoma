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
]  # pragma: no cover


this = sys.modules[__name__]  # pragma: no cover


for field_name in field_names:  # pragma: no cover

    setattr(
        this,
        field_name,
        type(field_name, (ExampleMixin, getattr(fields, field_name)), {}),
    )


class DecimalField(NumericExampleMixin, fields.DecimalField):  # pragma: no cover
    pass


@extend_schema_field(OpenApiTypes.UUID)  # pragma: no cover
class UUIDField(ExampleMixin, fields.UUIDField):  # pragma: no cover
    pass


class IntegerField(NumericExampleMixin, fields.IntegerField):  # pragma: no cover
    pass


class FloatField(NumericExampleMixin, fields.FloatField):  # pragma: no cover
    pass


class RegexField(RegexExampleMixin, fields.RegexField):  # pragma: no cover
    pass


class MACAddressField(RegexExampleMixin, fields.CharField):  # pragma: no cover
    def __init__(self, **kwargs) -> None:
        self.regex = "^([0-9A-F]{2}:){5}([0-9A-F]{2})|([0-9A-F]{2}-){5}([0-9A-F]{2})$"
        self.validators = [validators.RegexValidator(self.regex)]
        super().__init__(**kwargs)


@extend_schema_field(OpenApiTypes.DATE)  # pragma: no cover
class DateField(ExampleMixin, fields.DateField):  # pragma: no cover
    pass


@extend_schema_field(OpenApiTypes.TIME)  # pragma: no cover
class TimeField(ExampleMixin, fields.TimeField):  # pragma: no cover
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
)  # pragma: no cover
class IPAddressField(ExampleMixin, fields.IPAddressField):  # pragma: no cover
    pass


@extend_schema_field(field={"format": "tel"})  # pragma: no cover
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


class MoneyField(NumericExampleMixin, MoneyField):  # pragma: no cover
    pass


class ChoiceField(ExampleMixin, fields.ChoiceField):
    def __init__(self, choices, **kwargs):
        if isinstance(choices, dict):
            self.original_choices = list(choices.items())
        else:
            self.original_choices = choices
        super().__init__(choices, **kwargs)
