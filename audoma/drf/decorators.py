from functools import wraps

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.decorators import action

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


# TODO - add documentation
def audoma_action(
        methods=None, detail=None, url_path=None, url_name=None, response=None, collector=None,
        collectors={}, responses={}, validate_collector=True,**kwargs
    ):
    framework_decorator = action(methods=methods, detail=detail, url_path=url_path, url_name=url_name, **kwargs)
    def decorator(func):
        # apllying drf action decorator on function
        # TODO - make this more readable and cleaner
        func = framework_decorator(func)
        if collectors:
            setattr(func, 'collectors', collectors)
        elif collector:
            setattr(func, 'collectors', collector)
        
        if responses:
            setattr(func, 'responses', responses)
        elif response:
            setattr(func, 'responses', response)

        @wraps(func)
        def wrapper(view, request, *args, **kwargs):

            collect_serializer_class = extract_operation(
                collector, collectors, request, operation_category="collect"
            )

            collect_serializer_class = collect_serializer_class or view.get_serializer_class()
            
            if collect_serializer_class:
                collect_serializer = collect_serializer_class(data=request.data)
                if validate_collector:
                    collect_serializer.is_valid(raise_exception=True)
                kwargs['collect_serializer'] = collect_serializer

            instance, code = func(view, request, *args, **kwargs)

            response_operation = extract_operation(
                response, responses, request, code=code
            )
            return apply_response_operation(
                response_operation, instance, code, request, view
            )
        return wrapper

    return decorator
