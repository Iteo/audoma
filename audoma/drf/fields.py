import random

import exrex
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from phonenumber_field import serializerfields
from rest_framework import fields
from rest_framework.fields import *  # noqa: F403, F401

from django.core import validators

from audoma.drf.mixins import ExampleMixin


@extend_schema_field(
    field={"type": "number", "example": round(random.uniform(0, 1000), 2)}
)
class DecimalField(ExampleMixin, fields.DecimalField):
    pass


@extend_schema_field(OpenApiTypes.UUID)
class UUIDField(ExampleMixin, fields.UUIDField):
    pass


@extend_schema_field(field={"example": random.randint(1, 1000)})
class IntegerField(ExampleMixin, fields.IntegerField):
    pass


@extend_schema_field(field={"example": random.uniform(0, 1000)})
class FloatField(ExampleMixin, fields.FloatField):
    pass


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


@extend_schema_field(field={"format": "tel", "example": "+1 8888888822"})
class PhoneNumberField(ExampleMixin, serializerfields.PhoneNumberField):
    pass


class ChoiceField(fields.ChoiceField):
    def __init__(self, choices, **kwargs):
        if isinstance(choices, dict):
            self.original_choices = list(choices.items())
        else:
            self.original_choices = choices
        super().__init__(choices, **kwargs)
