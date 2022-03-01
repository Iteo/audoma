import exrex
from audoma.drf.mixins import ExampleMixin
from django.core import validators
from django.utils.functional import lazy
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from phonenumber_field import serializerfields
from rest_framework import fields
from rest_framework.fields import *


@extend_schema_field(OpenApiTypes.DECIMAL)
class DecimalField(ExampleMixin, fields.DecimalField):
    pass


@extend_schema_field(OpenApiTypes.UUID)
class UUIDField(ExampleMixin, fields.UUIDField):
    pass


@extend_schema_field(OpenApiTypes.INT)
class IntegerField(ExampleMixin, fields.IntegerField):
    pass


@extend_schema_field(OpenApiTypes.FLOAT)
class FloatField(ExampleMixin, fields.FloatField):
    pass


class RegexField(ExampleMixin, fields.RegexField):

    def __init__(self, regex, **kwargs):
        if 'example' not in kwargs:
            kwargs['example'] = lazy(lambda: str(exrex.getone(regex)), str)()
        super().__init__(regex, **kwargs)


class MACAddressField(ExampleMixin, fields.CharField):

    def __init__(self, **kwargs):
        self.regex = "^([0-9A-F]{2}:){5}([0-9A-F]{2})|([0-9A-F]{2}-){5}([0-9A-F]{2})$"
        self.validarors = [validators.RegexValidator(self.regex)]
        if 'example' not in kwargs:
            kwargs['example'] = lazy(lambda: str(exrex.getone(self.regex)), str)()
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
        "example": lazy(lambda: str(exrex.getone("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")), str)()
    }
)
class IPAddressField(ExampleMixin, fields.IPAddressField):
    pass


@extend_schema_field(
    field={
        "format": "tel",
        "example": lazy(lambda: str("+1 8888888822"), str)()
    }
)
class PhoneNumberField(ExampleMixin, serializerfields.PhoneNumberField):
    pass
