import sys

from django.db import models
from django.db.models.fields import __all__ as model_fields

from .mixins import ExampleMixin


this = sys.modules[__name__]


for field_name in model_fields:
    try:

        class Field(ExampleMixin, getattr(models, field_name)):
            pass

        Field.__name__ = field_name
        setattr(this, field_name, Field)
    except TypeError:
        pass
