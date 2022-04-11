import logging
from dataclasses import dataclass
from functools import wraps
from inspect import isclass
from typing import (
    List,
    Type,
    Union,
)

from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

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
    responses: Union[dict, BaseSerializer, str]
    collectors: Union[dict, BaseSerializer]
    errors: List[Union[Exception, Type[Exception]]]


class AudomaAction:
    def _sanitize_error(
        self, _errors: List[Union[Exception, Type[Exception]]]
    ) -> List[Union[Exception, Type[Exception]]]:
        if not _errors:
            return _errors
        instances = []
        types = []
        sanitized_errors = []

        for error in _errors:
            if isclass(error):
                types.append(error)
            elif isinstance(error, Exception):
                instances.append(error)
            else:
                raise ImproperlyConfigured(
                    f"Something that is not an Exception instance or class has been passed \
                        to AudomaAction errors list. The value which caused exception: {error}"
                )
        # check if there are no repetitions
        for instance in instances:
            if type(instance) in types:
                exception = ImproperlyConfigured(
                    f"Something that is not an Exception instance or class has been passed \
                        to AudomaAction errors list. The value which caused exception: {error}"
                )
                if project_settings.DEBUG:
                    raise exception
                logger.error(str(exception))
            else:
                sanitized_errors.append(instance)

        sanitized_errors += types
        return sanitized_errors

    def __init__(
        self,
        collectors: Union[dict, BaseSerializer] = None,
        responses: Union[dict, BaseSerializer, str] = None,
        errors: List[Union[Exception, Type[Exception]]] = None,
        validate_collector: bool = True,
        ignore_view_collectors: bool = False,
        **kwargs,
    ) -> None:
        """
        This is a custom action decorator which allows to define collectors, responses and errors.
        This decorator also applies the collect serializer if such has been defined.
        It also prevents from raising not defined errors, so if you want to raise an exception
        its' object or class has to be passed into AudomaAction decorator.

            * collectors - collect serializers, it may be passed as a dict: {'http_method': serializer_class}
                            or just as a serializer_class. Those serializer are being used to
                            collect data from user.
                            NOTE: - it is not possible to define collectors for SAFE_METHODS
            * responses - response serializers/messages, it may be passed as a dict in three forms:
                        * {'http_method': serializer_class}
                        * {'http_method': {status_code: serializer_class, status_code: serializer_class}}
                        * {status_code: serializer_class}
                        or just as a serializer_class
            * errors - list of exception objects, list of exceptions which may be raised in decorated method.
                        'AudomaAction' will not allow raising any other exceptions than those
            * validate_collector - by default set to True, it specifies if collectors serializer
                        should be validated in the decorator, or not.
            * ignore_view_collectors - If set to True, decorator is ignoring view collect serializers.
                        May be useful if we don't want to falback to default view collect serializer retrieval.
        """

        # get rid of serializer_class from kwargs if passed
        self.collectors = collectors or {}
        self.responses = responses or {}
        self.errors = self._sanitize_error(errors) or []
        self.validate_collector = validate_collector
        self.ignore_view_collectors = ignore_view_collectors

        self.kwargs = kwargs
        self.methods = kwargs.get("methods")
        self.framework_decorator = action(**kwargs)
        self.operation_extractor = OperationExtractor(collectors, responses, errors)

        # validate methods
        modify_methods = [
            method for method in self.methods if method not in SAFE_METHODS
        ]

        if not modify_methods and collectors:
            raise ImproperlyConfigured(
                "There should be no collectors defined if there are not create/update requests accepted."
            )

    def _get_error_instance_and_class(self, error: Union[Exception, Type[Exception]]):
        if isclass(error):
            error_class = error
            error_instance = error()
        else:
            error_instance = error
            error_class = type(error)
        return error_instance, error_class

    def _compare_errors_content(
        self,
        raised_error: Exception,
        compared_error: Exception,
        view: APIView,
        raised_error_class: Type[Exception],
    ) -> bool:
        handler = view.get_exception_handler()
        handler_context = view.get_exception_handler_context()
        raised_error_result = handler(raised_error, handler_context)
        compared_error_result = handler(compared_error, handler_context)

        unhandled_exception = (
            raised_error_result if not raised_error_result else compared_error_result
        )
        if not unhandled_exception:
            raise ImproperlyConfigured(
                f"Exception handler is unable to handle this exception: {type(unhandled_exception)}.\
                    To handle this type of exception you should write custom exception handler."
            )

        assert all(
            getattr(raised_error_result, attr) == getattr(compared_error_result, attr)
            for attr in ["status_code", "data", "headers"]
        ), f"Exception has not been defined {raised_error_class} \
            in AudomaAction decorator errors for action: {view.action}. \
            Audoma allows only to raise defined exceptions \
            Please define proper exception instance or proper exception class"

    def _process_error(
        self,
        processed_error: Union[Exception, Type[Exception]],
        errors: List[Union[Exception, Type[Exception]]],
        view: APIView,
    ) -> None:
        (
            processed_error_instance,
            processed_error_class,
        ) = self._get_error_instance_and_class(processed_error)
        no_class_match = False
        try:
            for error in errors:
                error_instance, error_class = self._get_error_instance_and_class(error)
                # This causes the issue, because this will not throw error for no matching class
                if not processed_error_class == error_class:
                    no_class_match = True
                    continue

                no_class_match = False
                # compare content only if defined error is an instance, if it is a class, all
                # class instances are valid
                if not isclass(error):
                    self._compare_errors_content(
                        processed_error_instance,
                        error_instance,
                        view,
                        processed_error_class,
                    )

                break

            assert (
                not no_class_match
            ), f"There is no class or instance of {processed_error_class} \
                defined in AudomaAction errors."

        except AssertionError as e:
            if project_settings.DEBUG:
                raise e
            logger.error(str(e))
            raise processed_error
        else:
            raise processed_error

    def __call__(self, func) -> Response:
        func._audoma = AudomaArgs(
            collectors=self.collectors, responses=self.responses, errors=self.errors
        )
        # apply action decorator
        func = self.framework_decorator(func)

        @wraps(func)
        def wrapper(view, request, *args, **kwargs):
            # extend errors too allow default errors occurance
            errors = func._audoma.errors
            errors += audoma_settings.COMMON_API_ERRORS + getattr(
                project_settings, "COMMON_API_ERRORS", []
            )

            if request.method not in SAFE_METHODS:
                collect_serializer_class = self.operation_extractor.extract_operation(
                    request, operation_category="collect"
                )

                if not collect_serializer_class and not self.ignore_view_collectors:
                    collect_serializer = view.get_serializer_class()

                if collect_serializer_class:
                    collect_serializer = collect_serializer_class(data=request.data)
                    if self.validate_collector:
                        collect_serializer.is_valid(raise_exception=True)
                    kwargs["collect_serializer"] = collect_serializer
            try:
                instance, code = func(view, request, *args, **kwargs)
            except Exception as processed_error:
                self._process_error(processed_error, errors, view)

            response_operation = self.operation_extractor.extract_operation(
                request, code=code
            )

            assert (
                code is not None
            ), "Status code has not been returned to audoma action."

            assert (
                isinstance(response_operation, str) or instance is not None
            ), "Instance \
            returned in AudomaAction decorated method may not be None if \
            response operation is not str message"

            return apply_response_operation(
                response_operation, instance, code, view, many=not func.detail
            )

        return wrapper
