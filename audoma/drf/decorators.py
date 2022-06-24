from functools import wraps
from typing import (
    Any,
    Callable,
)

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


def document_and_format(serializer_or_field: Any) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @extend_schema_field(serializer_or_field)
        def wrapper(*args, **kwargs) -> Any:
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
