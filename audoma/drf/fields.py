"""
This module is an override for default drf's field module.
Most of those fields, are providing additional example functionality,
and also has defined schema type.
"""

import sys
from typing import Any

import exrex
import phonenumbers
from djmoney.contrib.django_rest_framework import MoneyField
from drf_extra_fields import fields as extra_fields
from drf_extra_fields.fields import *  # noqa: F403, F401
from drf_spectacular.drainage import set_override
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from phonenumber_field import serializerfields
from phonenumber_field.phonenumber import to_python
from psycopg2._range import (
    DateRange,
    DateTimeTZRange,
    NumericRange,
)
from rest_framework import fields
from rest_framework.fields import *  # noqa: F403, F401

from django.core import validators

from audoma.example_generators import generate_lorem_ipsum
from audoma.mixins import (
    Base64ExampleMixin,
    DateExampleMixin,
    DateTimeExampleMixin,
    ExampleMixin,
    NumericExampleMixin,
    RangeExampleMixin,
    RegexExampleMixin,
    TimeExampleMixin,
)


field_names = [
    "BooleanField",
    "NullBooleanField",
    "EmailField",
    "SlugField",
    "URLField",
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
class DateField(DateExampleMixin, fields.DateField):
    pass


@extend_schema_field(OpenApiTypes.TIME)
class TimeField(TimeExampleMixin, fields.TimeField):
    pass


class DateTimeField(DateTimeExampleMixin, fields.DateTimeField):
    ...


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
        if field is not None and not isinstance(field, fields.Field):
            raise ValueError(
                f"Incorrect type of field, field \
                    must be an instance of rest_framework.fields.Field.\
                        Passed value: {field}"
            )
        return field

    def __init__(
        self, *args, method_name=None, field=None, writable=False, **kwargs
    ) -> None:
        self.method_name = method_name
        self.field = self._parse_field(field)
        writable = writable
        if writable and self.field is None:
            raise ValueError("Writable SerializerMethodField must have field defined.")

        kwargs["source"] = "*"
        kwargs["read_only"] = not writable
        super().__init__(*args, **kwargs)

    def __getattribute__(self, name: str) -> Any:
        if (
            name
            not in [
                "validators",
                "get_validators",
                "run_validators",
                "validate_empty_values",
            ]
            or not self.field
        ):
            return super().__getattribute__(name)

        return getattr(self.field, name)

    def bind(self, field_name, parent):
        # The method name defaults to `get_{field_name}`.
        if self.method_name is None:
            self.method_name = "get_{field_name}".format(field_name=field_name)
        super().bind(field_name, parent)
        if self.field is not None:
            set_override(self, "field", self.field)
        # set params for child field
        self.field.parent = self.parent
        self.field.field_name = self.field_name

    def to_representation(self, obj):
        method = getattr(self.parent, self.method_name)
        value = method(obj)
        if not self.field or value is None:
            return value
        else:
            return self.field.to_representation(value)

    def get_default(self):
        return {self.field_name: self.field.get_default}

    def to_internal_value(self, data):
        return {self.field_name: self.field.to_internal_value(data)}

    def run_validation(self, data):
        return {self.field_name: self.field.run_validation(data)}


class Base64ImageField(Base64ExampleMixin, extra_fields.Base64ImageField):
    ...


# TODO - provide example for this one
# class HybridImageField(HybridImageField):
#    ...


class Base64FileField(Base64ExampleMixin, extra_fields.Base64FileField):
    ...


class RangeField(RangeExampleMixin, extra_fields.RangeField):
    ...


@extend_schema_field(IntegerField())
class IntegerRangeField(RangeField):
    child_class = IntegerField
    default_child_attrs = {}
    range_type = NumericRange


@extend_schema_field(FloatField())
class FloatRangeField(RangeField):
    child_class = FloatField
    default_child_attrs = {}
    range_type = NumericRange


@extend_schema_field(DecimalField(**{"max_digits": None, "decimal_places": None}))
class DecimalRangeField(RangeField):
    child_class = DecimalField
    default_child_attrs = {"max_digits": None, "decimal_places": None}
    range_type = NumericRange


@extend_schema_field(DateTimeField())
class DateTimeRangeField(RangeField):
    child_class = DateTimeField
    default_child_attrs = {}
    range_type = DateTimeTZRange


@extend_schema_field(DateField())
class DateRangeField(RangeField):
    child_class = DateField
    default_child_attrs = {}
    range_type = DateRange
