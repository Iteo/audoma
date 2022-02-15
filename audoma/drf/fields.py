from rest_framework.fields import *
from django.core import validators
from rest_framework import fields
from django.utils.functional import lazy
from audoma.drf.mixins import ExampleMixin
import exrex
from phonenumber_field import serializerfields
from drf_spectacular.utils import extend_schema_field, OpenApiExample, extend_schema_serializer
from drf_spectacular.types import OpenApiTypes

import random
import uuid


@extend_schema_field(OpenApiTypes.DECIMAL)
class DecimalField(ExampleMixin, fields.DecimalField):

    def to_representation(self, value):
        return 123.234


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


# @extend_schema_field(OpenApiTypes.IP4, 'my_name')
@extend_schema_field(
    field={
        "type": "IPv4 or IPv6",
        "example": lazy(lambda: str(exrex.getone("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")), str)()
    }
)
class IPAddressField(ExampleMixin, fields.IPAddressField):
    pass


@extend_schema_field(
    field={
        "type": "tel",
        "example": lazy(lambda: str("+1 8888888822"), str)()
    }
)
class PhoneNumberField(ExampleMixin, serializerfields.PhoneNumberField):
    pass
