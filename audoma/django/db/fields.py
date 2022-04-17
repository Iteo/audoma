import sys

import phonenumbers
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

    class Field(ModelExampleMixin, getattr(models, field_name)):
        pass

    Field.__name__ = field_name
    setattr(this, field_name, Field)


__all__.append("PhoneNumberField")


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
