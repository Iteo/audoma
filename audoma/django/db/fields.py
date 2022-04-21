import sys

import phonenumbers
from djmoney.models.fields import (
    CurrencyField,
    MoneyField,
)
from djmoney.utils import get_currency_field_name
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import to_python

from django.db import models
from django.db.models.fields import (  # noqa: F401
    BLANK_CHOICE_DASH,
    NOT_PROVIDED,
    __all__,
)

from audoma.example_generators import generate_lorem_ipsum

from .mixins import ModelExampleMixin


this = sys.modules[__name__]


for field_name in __all__:
    if field_name in ["BLANK_CHOICE_DASH", "NOT_PROVIDED"]:
        continue

    setattr(
        this,
        field_name,
        type(field_name, (ModelExampleMixin, getattr(models, field_name)), {}),
    )


__all__.extend(["MoneyField", "CurrencyField", "PhoneNumberField"])


class CurrencyField(ModelExampleMixin, CurrencyField):
    pass


class MoneyField(ModelExampleMixin, MoneyField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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


class PhoneNumberField(ModelExampleMixin, PhoneNumberField):
    def __init__(self, *args, region=None, **kwargs):
        super().__init__(*args, region=region, **kwargs)
        if not kwargs.get("example", None):
            number = phonenumbers.example_number(region)
            self.example = str(to_python(number))


class CharField(ModelExampleMixin, models.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        max_length = kwargs.get("max_length", 80)
        if not kwargs.get("example", None) and max_length:
            self.example = generate_lorem_ipsum(max_length=max_length)


class TextField(ModelExampleMixin, models.TextField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not kwargs.get("example", None):
            self.example = generate_lorem_ipsum()
