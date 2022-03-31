import sys

import exrex
import phonenumbers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from phonenumber_field import serializerfields
from phonenumber_field.phonenumber import to_python
from rest_framework import fields
from rest_framework.fields import *  # noqa: F403, F401

from django.core import validators

from audoma.drf.mixins import (
    ExampleMixin,
    NumericExampleMixin,
    RegexExampleMixin,
)


field_names = [
    "BooleanField",
    "NullBooleanField",
    "CharField",
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

    class Field(ExampleMixin, getattr(fields, field_name)):
        pass

    Field.__name__ = field_name
    setattr(this, field_name, Field)


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
    def __init__(self, **kwargs):
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
    def __init__(self, *args, **kwargs):
        example = kwargs.pop("example", None)
        if not example:
            number = phonenumbers.example_number(None)
            example = str(to_python(number))
        super().__init__(*args, example=example, **kwargs)
