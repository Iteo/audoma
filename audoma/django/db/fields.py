import random
import sys

from djmoney.models.fields import (
    CurrencyField,
    MoneyField,
)
from djmoney.utils import get_currency_field_name

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
    def __init__(self, *args, **kwargs):

        default = kwargs.get("default", None)
        if default and str(default) != "XYZ":
            self.example = default
        elif kwargs.get("choices", None):
            self.example = random.choice(kwargs["choices"])[0]
        else:
            self.example = "XYZ"
        super().__init__(*args, **kwargs)


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
            editable=False,
            choices=self.currency_choices,
            null=self.default_currency is None,
        )
        currency_field.creation_counter = self.creation_counter - 1
        currency_field_name = get_currency_field_name(name, self)
        cls.add_to_class(currency_field_name, currency_field)
        self._currency_field = currency_field
