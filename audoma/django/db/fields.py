import random
import sys

from djmoney.models.fields import (
    CurrencyField,
    MoneyField,
)
from djmoney.utils import get_currency_field_name

from django.conf import settings
from django.db import models
from django.db.models.fields import (  # noqa: F401
    BLANK_CHOICE_DASH,
    NOT_PROVIDED,
    __all__,
)

from .mixins import ModelExampleMixin


this = sys.modules[__name__]


for field_name in __all__:
    if field_name in ["BLANK_CHOICE_DASH", "NOT_PROVIDED"]:
        continue

    class Field(ModelExampleMixin, getattr(models, field_name)):
        pass

    Field.__name__ = field_name
    setattr(this, field_name, Field)


__all__.extend(["MoneyField", "CurrencyField"])


class CurrencyField(ModelExampleMixin, CurrencyField):
    pass


class MoneyField(ModelExampleMixin, MoneyField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_currency_field(self, cls, name):
        """
        Adds CurrencyField instance to a model class and creates example in documentation.
        """

        if self.default_currency and str(self.default_currency) != "XYZ":
            example = self.default_currency
        elif getattr(settings, "CURRENCIES", None):
            example = random.choice(settings.CURRENCIES)
        else:
            example = "XYZ"

        currency_field = CurrencyField(
            price_field=self,
            max_length=self.currency_max_length,
            default=self.default_currency,
            editable=False,
            choices=self.currency_choices,
            null=self.default_currency is None,
            example=example,
        )
        currency_field.creation_counter = self.creation_counter - 1
        currency_field_name = get_currency_field_name(name, self)
        cls.add_to_class(currency_field_name, currency_field)
        self._currency_field = currency_field
