import sys

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
