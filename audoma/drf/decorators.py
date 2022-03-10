from functools import wraps

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.decorators import action

from audoma.behaviour import (
    CollectBehaviourFactory,
    ResponsesBehaviourFactory,
    apply_behaviours,
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
    methods=None,
    detail=None,
    url_path=None,
    url_name=None,
    response=None,
    collector=None,
    collectors={},
    responses={},
    **kwargs
):
    framework_decorator = action(
        methods=methods, detail=detail, url_path=url_path, url_name=url_name, **kwargs
    )
    collect_behaviour_factory = CollectBehaviourFactory()
    response_behaviour_factory = ResponsesBehaviourFactory()
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
            instance, code = func(view, request, *args, **kwargs)

            collect_behaviour = collect_behaviour_factory.create_behaviour(
                collector, collectors, request, code
            )
            response_behaviour = response_behaviour_factory.create_behaviour(
                response, responses, request, code
            )
            # the result should be transferred into Response
            return apply_behaviours(
                collect_behaviour, response_behaviour, instance, code, request, view
            )
        return wrapper

    return decorator
