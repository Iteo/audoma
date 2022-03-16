import random
from unicodedata import decimal

import exrex
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from phonenumber_field import serializerfields
from rest_framework import fields
from rest_framework.fields import *  # noqa: F403, F401

from django.core import validators
from django.utils.functional import lazy

from audoma.drf.mixins import ExampleMixin


class DecimalField(ExampleMixin, fields.DecimalField):
    def __init__(self, **kwargs):
        if "example" not in kwargs:
            decimal_places = kwargs.get("decimal_places", None) or 2
            min_value = kwargs.get("min_value", None) or 0
            max_value = kwargs.get("max_value", None) or 1000
            kwargs["example"] = round(
                random.uniform(min_value, max_value), decimal_places
            )
        super().__init__(**kwargs)


@extend_schema_field(OpenApiTypes.UUID)
class UUIDField(ExampleMixin, fields.UUIDField):
    pass


class IntegerField(ExampleMixin, fields.IntegerField):
    def __init__(self, **kwargs):
        if "example" not in kwargs:
            min_value = kwargs.get("min_value", None) or 0
            max_value = kwargs.get("max_value", None) or 1000
            kwargs["example"] = random.randint(min_value, max_value)
        super().__init__(**kwargs)


class FloatField(ExampleMixin, fields.FloatField):
    def __init__(self, **kwargs):
        if "example" not in kwargs:
            min_value = kwargs.get("min_value", None) or 0
            max_value = kwargs.get("max_value", None) or 1000
            kwargs["example"] = random.uniform(min_value, max_value)
        super().__init__(**kwargs)


class RegexField(ExampleMixin, fields.RegexField):
    def __init__(self, regex, **kwargs):
        if "example" not in kwargs:
            kwargs["example"] = str(exrex.getone(regex))
        super().__init__(regex, **kwargs)


class MACAddressField(ExampleMixin, fields.CharField):
    def __init__(self, **kwargs):
        self.regex = "^([0-9A-F]{2}:){5}([0-9A-F]{2})|([0-9A-F]{2}-){5}([0-9A-F]{2})$"
        self.validarors = [validators.RegexValidator(self.regex)]
        if "example" not in kwargs:
            kwargs["example"] = str(exrex.getone(self.regex))
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


@extend_schema_field(field={"format": "tel", "example": "555-2310"})
class PhoneNumberField(ExampleMixin, serializerfields.PhoneNumberField):
    pass
