"""Audoma Django model Fields
This module contains all the fields from Django models with additional functionality.
By inheriting from Audoma Mixins, an example is generated for each field (i.e. FloatField will have
example generated based on field's min and max values).
We can define custom example by simply passing `example` as an argument to the field.
"""

import random
import sys

import phonenumbers
from djmoney.models import fields as djmoney_fields
from djmoney.utils import get_currency_field_name
from macaddress.fields import MACAddressField
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import to_python

from django.db import models
from django.db.models.fields import (  # noqa: F401
    BLANK_CHOICE_DASH,
    NOT_PROVIDED,
    __all__,
)

from audoma.django import forms
from audoma.example_generators import generate_lorem_ipsum
from audoma.mixins import ModelExampleMixin


try:
    from django.db.models import JSONField
except ImportError:
    try:
        from jsonfield import JSONField
    except ImportError as err:
        raise ImportError(
            "You are using old version of Django that doesn't support JSONField. Please install django-jsonfield"
        ) from err


this = sys.modules[__name__]


for field_name in __all__:
    if field_name in ["BLANK_CHOICE_DASH", "NOT_PROVIDED"]:
        continue

    setattr(
        this,
        field_name,
        type(field_name, (ModelExampleMixin, getattr(models, field_name)), {}),
    )


__all__.extend(["MoneyField", "CurrencyField", "PhoneNumberField", "MACAddressField"])


class CurrencyField(ModelExampleMixin, djmoney_fields.CurrencyField):
    def __init__(self, *args, **kwargs) -> None:
        default = kwargs.get("default", None)
        if default and str(default) != "XYZ":
            self.example = default
        elif kwargs.get("choices", None):
            self.example = random.choice(kwargs["choices"])[0]
        else:
            self.example = "XYZ"
        super().__init__(*args, **kwargs)


class MoneyField(ModelExampleMixin, djmoney_fields.MoneyField):
    def add_currency_field(self, cls, name):
        """
        Adds CurrencyField instance to a model class and creates example in documentation.
        """

        currency_field = CurrencyField(
            price_field=self,
            max_length=self.currency_max_length,
            default=self.default_currency,
            choices=self.currency_choices,
            null=self.default_currency is None,
        )
        currency_field.creation_counter = self.creation_counter - 1
        currency_field_name = get_currency_field_name(name, self)
        cls.add_to_class(currency_field_name, currency_field)
        self._currency_field = currency_field

    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.MoneyField,
            "decimal_places": self.decimal_places,
        }
        defaults.update(kwargs)
        if self._has_default:
            defaults["default_amount"] = self.default.amount
        return super(djmoney_fields.MoneyField, self).formfield(**defaults)


class PhoneNumberField(ModelExampleMixin, PhoneNumberField):
    def __init__(self, *args, region=None, **kwargs) -> None:
        super().__init__(*args, region=region, **kwargs)
        if not kwargs.get("example", None):
            number = phonenumbers.example_number(region)
            self.example = str(to_python(number))


class CharField(ModelExampleMixin, models.CharField):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        max_length = kwargs.get("max_length", 80)
        if not kwargs.get("example", None) and max_length:
            self.example = generate_lorem_ipsum(max_length=max_length)


class TextField(ModelExampleMixin, models.TextField):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not kwargs.get("example", None):
            self.example = generate_lorem_ipsum()


class MACAddressField(ModelExampleMixin, MACAddressField):
    pass


class JSONField(ModelExampleMixin, JSONField):
    pass


if "JSONField" not in __all__:
    __all__.append("JSONField")
