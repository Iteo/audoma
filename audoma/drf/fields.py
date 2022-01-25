from rest_framework.fields import *
from rest_framework import fields
from django.utils.functional import lazy

import random
import uuid


class DecimalField(fields.DecimalField):
    class Meta:
        swagger_schema_fields = {
            "example": lazy(lambda: "%.2f" % (random.random() * random.randint(1, 1000)), str)()
        }


class UUIDField(fields.UUIDField):
    class Meta:
        swagger_schema_fields = {
            "example": lazy(lambda: str(uuid.uuid4()), str)()
        }


class IntegerField(fields.IntegerField):
    class Meta:
        swagger_schema_fields = {
            "example": lazy(lambda: random.randint(1, 1000), int)()
        }


class FloatField(fields.FloatField):
    class Meta:
        swagger_schema_fields = {
            "example": lazy(lambda: (random.random() * random.randint(1, 1000)), float)()
        }
