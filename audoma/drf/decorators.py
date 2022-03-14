from functools import wraps
from urllib import response
from venv import create

from django.core.exceptions import ImproperlyConfigured
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS

from audoma.operations import (
    extract_operation, 
    apply_response_operation
)


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


def document_serializers(collectors={}, responses={}, methods=None):
    """
        This method simply sets collectors and responses function attributes.
        This may be used for method in views, where there is no reason to use audoma_action.
    """
    # TODO - change this
    modify_methods  = [method for method in methods if method not in SAFE_METHODS]

    if not modify_methods and collectors:
        raise ImproperlyConfigured(
            "There should be no collectors defined if there are not create/update requests accepted."
        )

    def decorator(func):
        func.collectors = collectors
        func.responses = responses
        return func
        
    return decorator

    
def audoma_action(
       collectors={}, responses={}, validate_collector=True,**kwargs
    ):
    """
        This is a custom action tag which allows to define collectors and responses.
        This tag also applies the collect serializer, and validates the input.
        # TODO
    """
    methods = kwargs.get('methods')
    framework_decorator = action(**kwargs)
    serializers_decorator = document_serializers(collectors=collectors, responses=responses, methods=methods)
    def decorator(func):
        # apply other decorators
        func = serializers_decorator(func)
        func = framework_decorator(func)

        @wraps(func)
        def wrapper(view, request, *args, **kwargs):
            # TODO does not allow returning error codes, which are not defined
            if collectors is not None and request.method not in SAFE_METHODS:
                collect_serializer_class = extract_operation(
                    collectors, request, operation_category="collect"
                )
                
                collect_serializer_class = collect_serializer_class or view.get_serializer_class()
                
                if collect_serializer_class:
                    collect_serializer = collect_serializer_class(data=request.data)
                    if validate_collector:
                        collect_serializer.is_valid(raise_exception=True)
                    kwargs['collect_serializer'] = collect_serializer

            instance, code = func(view, request, *args, **kwargs)

            response_operation = extract_operation(
                responses, request, code=code
            )
            return apply_response_operation(
                response_operation, instance, code, view, many=not func.detail
            )
        return wrapper
    return decorator
