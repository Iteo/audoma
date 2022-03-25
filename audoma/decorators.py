import json
import logging
from dataclasses import dataclass
from functools import wraps

from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.permissions import SAFE_METHODS

from django.conf import settings as project_settings
from django.core.exceptions import ImproperlyConfigured

from audoma import settings as audoma_settings
from audoma.operations import (
    OperationExtractor,
    apply_response_operation,
)


logger = logging.getLogger(__name__)


@dataclass
class AudomaArgs:
    responses: dict
    collectors: dict
    errors: list


def __verify_error(processed_error, errors, func):
    same_class_errors = []
    for error in errors:
        if isinstance(error, type):
            if error == processed_error.__class__:
                raise processed_error
            else:
                continue

        elif (
            isinstance(error, APIException)
            and error.__class__ == processed_error.__class__
        ):
            same_class_errors.append(error)

    if same_class_errors:
        # compare errors details
        for error in same_class_errors:
            if json.dumps(error.__dict__) == json.dumps(processed_error.__dict__):
                raise error

        if project_settings.DEBUG:
            raise ValueError(
                f"Exception has not been defined {processed_error.__class__} \
                    in audoma_action tag errors for function: {func.__name__}. \
                    Audoma allows only to raise defined exceptions \
                    Please define proper exception instance or proper exception class"
            )

        logger.exception("Undefined error: {error} has been raised in {func.__name__}")
        raise processed_error

    raise ValueError(
        f"Exception has not been defined {processed_error.__class__} \
            in audoma_action tag errors for function: {func.__name__}. \
            Audoma allows only to raise defined exceptions \
            Please define proper exception instance or proper exception class"
    )


def audoma_action(
    collectors={}, responses={}, errors=[], validate_collector=True, **kwargs
):
    """
    This is a custom action tag which allows to define collectors, responses and errors.
    This tag also applies the collect serializer if such has been defined.
    It also prevents from raising not defined error, so if you want to raise an exception
    its' object has to be passed into audoma_action decorator.

        * collectors - collect serializers, it may be passed as a dict: {'http_method': serializer_class}
                        or just as a serializer_class. Those serializer are being used to collect data from user.
                        NOTE: - it is not possible to define collectors for SAFE_METHODS
        * responses - response serializers/messages, it may be passed as a dict in three forms:
                    * {'http_method': serializer_class}
                    * {'http_method': {status_code: serializer_class, status_code: serializer_class}}
                    * {status_code: serializer_class}
                    or just as a serializer_class
        * errors - list of exception objects, list of exceptions which may be raised in decorated method.
                    'audoma_action' will not allow raising any other exceptions than those
        * validate_collector - by default set to True, it specifies if collectors serializer
                    should be validated in the decorator, or not.
    """
    assert isinstance(errors, list)

    # get rid of serializer_class from kwargs if passed
    kwargs.pop("serializer_class", None)

    methods = kwargs.get("methods")
    framework_decorator = action(**kwargs)
    operation_extractor = OperationExtractor(collectors, responses, errors)

    # validate methods
    modify_methods = [method for method in methods if method not in SAFE_METHODS]

    if not modify_methods and collectors:
        raise ImproperlyConfigured(
            "There should be no collectors defined if there are not create/update requests accepted."
        )

    def decorator(func):
        func._audoma = AudomaArgs(
            collectors=collectors, responses=responses, errors=errors
        )
        # apply action decorator
        func = framework_decorator(func)

        @wraps(func)
        def wrapper(view, request, *args, **kwargs):
            # extend errors too allow default errors occurance
            errors = func._audoma.errors
            errors += audoma_settings.COMMON_API_ERRORS + getattr(
                project_settings, "COMMON_API_ERRORS", []
            )

            if collectors is not None and request.method not in SAFE_METHODS:
                collect_serializer_class = operation_extractor.extract_operation(
                    request, operation_category="collect"
                )

                collect_serializer_class = (
                    collect_serializer_class or view.get_serializer_class()
                )

                if collect_serializer_class:
                    collect_serializer = collect_serializer_class(data=request.data)
                    if validate_collector:
                        collect_serializer.is_valid(raise_exception=True)
                    kwargs["collect_serializer"] = collect_serializer
            try:
                instance, code = func(view, request, *args, **kwargs)
            except APIException as processed_error:
                __verify_error(processed_error, errors, func)

            response_operation = operation_extractor.extract_operation(
                request, code=code
            )
            return apply_response_operation(
                response_operation, instance, code, view, many=not func.detail
            )

        return wrapper

    return decorator
