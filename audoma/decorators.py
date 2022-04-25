import logging
from dataclasses import dataclass
from functools import wraps
from inspect import isclass
from typing import (
    Any,
    Callable,
    Iterable,
    List,
    Tuple,
    Type,
    Union,
)

from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from django.conf import settings as project_settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model

from audoma import settings as audoma_settings
from audoma.operations import (
    OperationExtractor,
    apply_response_operation,
)


logger = logging.getLogger(__name__)


@dataclass
class AudomaArgs:
    results: Union[dict, BaseSerializer, str]
    collectors: Union[dict, BaseSerializer]
    errors: List[Union[Exception, Type[Exception]]]


class AudomaActionException(Exception):
    pass


class audoma_action:
    def _sanitize_kwargs(self, kwargs: dict) -> dict:
        if kwargs.get("serializer_class", None):
            raise ImproperlyConfigured(
                "serializer_class parameter is not allowed in audoma_action, \
                    use collectors and responses instead."
            )
        return kwargs

    def _sanitize_error(
        self, _errors: List[Union[Exception, Type[Exception]]]
    ) -> List[Union[Exception, Type[Exception]]]:
        """ "
        This methods sanitizes passed errors list.
        This prevents defining Exception Type and same Type instance in errors list.
        It also invokes method which validates if all erors in list are possible to handle by current handler.
        """
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
                        to audoma_action errors list. The value which caused exception: {error}"
                )

        # check if there are no repetitions
        for instance in instances:
            if type(instance) in types:
                raise ImproperlyConfigured(
                    f"Something that is not an Exception instance or class has been passed \
                        to audoma_action errors list. The value which caused exception: {error}"
                )
            else:
                sanitized_errors.append(instance)

        sanitized_errors += types
        return sanitized_errors

    def __init__(
        self,
        collectors: Union[dict, BaseSerializer] = None,
        results: Union[dict, BaseSerializer, str] = None,
        errors: List[Union[Exception, Type[Exception]]] = None,
        validate_collector: bool = True,
        ignore_view_collectors: bool = False,
        **kwargs,
    ) -> None:
        """
        This is a custom action decorator which allows to define collectors, results and errors.
        This decorator also applies the collect serializer if such has been defined.
        It also prevents from raising not defined errors, so if you want to raise an exception
        its' object or class has to be passed into audoma_action decorator.

            * collectors - collect serializers, it may be passed as a dict: {'http_method': serializer_class}
                            or just as a serializer_class. Those serializer are being used to
                            collect data from user.
                            NOTE: - it is not possible to define collectors for SAFE_METHODS
            * results - response serializers/messages, it may be passed as a dict in three forms:
                        * {'http_method': serializer_class}
                        * {'http_method': {status_code: serializer_class, status_code: serializer_class}}
                        * {status_code: serializer_class}
                        or just as a serializer_class
            * errors - list of exception objects, list of exceptions which may be raised in decorated method.
                        'audoma_action' will not allow raising any other exceptions than those
            * validate_collector - by default set to True, it specifies if collectors serializer
                        should be validated in the decorator, or not.
            * ignore_view_collectors - If set to True, decorator is ignoring view collect serializers.
                        May be useful if we don't want to falback to default view collect serializer retrieval.
        """
        self.collectors = collectors or {}
        self.results = results or {}
        self.validate_collector = validate_collector
        self.ignore_view_collectors = ignore_view_collectors

        try:
            self.errors = self._sanitize_error(errors) or []
            self.kwargs = self._sanitize_kwargs(kwargs) or {}
            self.methods = kwargs.get("methods")
            self.framework_decorator = action(**kwargs)
            self.operation_extractor = OperationExtractor(collectors, results, errors)
            if all(method in SAFE_METHODS for method in self.methods) and collectors:
                raise ImproperlyConfigured(
                    "There should be no collectors defined if there are not create/update requests accepted."
                )
        except ImproperlyConfigured as e:
            if project_settings.DEBUG:
                raise e
            logger.exception("audoma_action has been improperly configured.")

    def _get_error_instance_and_class(self, error: Union[Exception, Type[Exception]]):
        if isclass(error):
            error_class = error
            error_instance = error()
        else:
            error_instance = error
            error_class = type(error)
        return error_instance, error_class

    def _get_type_matched_exceptions(
        self,
        errors: List[Union[Exception, Type[Exception]]],
        processed_error_class: Type[Exception],
    ) -> List[Union[Exception, Type[Exception]]]:
        type_matched_exceptions = []
        for error in errors:
            error_instance, error_class = self._get_error_instance_and_class(error)

            if not processed_error_class == error_class:
                continue

            type_matched_exceptions.append((error, error_instance))

        if not type_matched_exceptions:
            raise AudomaActionException(
                f"There is no class or instance of {processed_error_class} \
                    defined in audoma_action errors."
            )
        return type_matched_exceptions

    def _compare_errors_content(
        self, raised_error: Exception, catched_error: Exception, view: APIView
    ) -> bool:
        handler = view.get_exception_handler()
        handler_context = view.get_exception_handler_context()
        raised_error_result = handler(raised_error, handler_context)
        catched_error_result = handler(catched_error, handler_context)

        if not raised_error_result:
            raise AudomaActionException(
                f"Current exception handler is unable to \
                handle raised exception: {type(raised_error)}.\
                To handle this type of exception you should write custom exception handler."
            )

        return all(
            getattr(raised_error_result, attr) == getattr(catched_error_result, attr)
            for attr in ["status_code", "data", "headers"]
        )

    def _get_error_match(
        self,
        type_matched_exceptions: List[Union[Exception, Type[Exception]]],
        processed_error_instance: Exception,
        view: APIView,
    ) -> Exception:
        ...

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
        error_match = False

        try:
            # get all errors with same class as raised exception
            type_matched_exceptions = self._get_type_matched_exceptions(
                errors, processed_error_class
            )
            for error, error_instance in type_matched_exceptions:
                if isclass(error):
                    error_match = True
                    break

                elif self._compare_errors_content(
                    processed_error_instance, error_instance, view
                ):
                    error_match = True
                    break
            if not error_match:
                raise AudomaActionException(
                    "Raised error: {processed_error_instance} has not been \
                        defined in audoma_action errors."
                )

        except AudomaActionException as e:
            if project_settings.DEBUG:
                raise e
            logger.exception(
                "Error has occured during audoma_action exception processing."
            )
        raise processed_error_instance

    def _retrieve_collect_serializer_class_with_config(
        self, request: Request, func: Callable, view: APIView
    ) -> Tuple[Type[BaseSerializer], bool, Any]:
        collect_serializer_class = None
        partial = False
        view_instance = None

        if request.method not in SAFE_METHODS:
            collect_serializer_class = self.operation_extractor.extract_operation(
                request, operation_category="collect"
            )

            if not collect_serializer_class and not self.ignore_view_collectors:
                collect_serializer_class = view.get_serializer_class()
            # Get object if collect serializer is used to update existing instance
            if func.detail and request.method in ["PUT", "PATCH"]:
                view_instance = view.get_object()
                partial = True if request.method.lower() == "patch" else False
            else:
                partial = False
                view_instance = None
        return collect_serializer_class, partial, view_instance

    def _action_return_checks(
        self,
        code: int,
        instance: Union[Iterable, str, APIException, Model],
        response_operation: Union[str, APIException, BaseSerializer],
    ) -> None:
        if code is None:
            raise AudomaActionException(
                "Status code has not been returned to audoma action."
            )

        if not isinstance(response_operation, str) and instance is None:
            raise AudomaActionException(
                "Instance returned in audoma_action decorated \
                    method may not be None if result operation is not str message"
            )

    def __call__(self, func: Callable) -> Response:
        func._audoma = AudomaArgs(
            collectors=self.collectors, results=self.results, errors=self.errors
        )
        # apply action decorator
        func = self.framework_decorator(func)

        @wraps(func)
        def wrapper(view: APIView, request: Request, *args, **kwargs):
            # extend errors too allow default errors occurance
            errors = func._audoma.errors
            errors += audoma_settings.COMMON_API_ERRORS + getattr(
                project_settings, "COMMON_API_ERRORS", []
            )
            (
                collect_serializer_class,
                partial,
                view_instance,
            ) = self._retrieve_collect_serializer_class_with_config(request, func, view)
            try:
                if collect_serializer_class:
                    collect_serializer = collect_serializer_class(
                        view_instance, data=request.data, partial=partial
                    )
                    if self.validate_collector:
                        collect_serializer.is_valid(raise_exception=True)
                    kwargs["collect_serializer"] = collect_serializer

                instance, code = func(view, request, *args, **kwargs)

            except Exception as processed_error:
                self._process_error(processed_error, errors, view)

            try:
                response_operation = self.operation_extractor.extract_operation(
                    request, code=code
                )

                self._action_return_checks(
                    code=code, instance=instance, response_operation=response_operation
                )
            except AudomaActionException as e:
                if project_settings.DEBUG:
                    raise e
                logger.exception(
                    "Error has occured during audoma_action \
                        processing action function execution result"
                )

            return apply_response_operation(
                response_operation, instance, code, view, many=not func.detail
            )

        return wrapper
