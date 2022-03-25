from functools import wraps
from urllib import response
from venv import create

from django.core.exceptions import ImproperlyConfigured
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


def document_and_format(serializer_or_field):
    def decorator(func):
        @wraps(func)
        @extend_schema_field(serializer_or_field)
        def wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            f = (
                serializer_or_field
                if isinstance(serializer_or_field, serializers.Field)
                else serializer_or_field()
            )
            f.parent = args[0]
            return f.to_representation(value) if value is not None else None

        return wrapper

    return decorator
