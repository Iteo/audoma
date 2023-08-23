import logging
from copy import deepcopy
from dataclasses import dataclass
from functools import wraps
from inspect import isclass
from typing import (
    Callable,
    Dict,
    Iterable,
    List,
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


logger = logging.getLogger(__name__)


SerializersConfig = Union[
    Dict[str, Dict[int, Union[str, Type[BaseSerializer]]]],
    Dict[str, Union[str, Type[BaseSerializer]]],
    str,
    Type[BaseSerializer],
]


@dataclass
class AudomaArgs:
    results: SerializersConfig
    collectors: SerializersConfig
    errors: List[Union[Exception, Type[Exception]]]
    results_many: bool
    collectors_many: bool


class AudomaActionException(Exception):
    pass


class audoma_action:
    """
    This is a custom action decorator which allows to define collectors, results and errors.
    This decorator also applies the collect serializer if such has been defined.
    It also prevents from raising not defined errors, so if you want to raise an exception
    its' object or class has to be passed into audoma_action decorator.

    Args:
        collectors - collect serializers, it may be passed as a dict: {'http_method': serializer_class}
                        or just as a serializer_class. Those serializer are being used to
                        collect data from user.
                        NOTE: - it is not possible to define collectors for SAFE_METHODS
        results - response serializers/messages, it may be passed as a dict in three forms:
                    * {'http_method': serializer_class}
                    * {'http_method': {status_code: serializer_class, status_code: serializer_class}}
                    * {status_code: serializer_class}
                    * just as a serializer_class
        errors - list of exception objects, list of exceptions which may be raised in decorated method.
                    'audoma_action' will not allow raising any other exceptions than those
        ignore_view_collectors - If set to True, decorator is ignoring view collect serializers.
                    May be useful if we don't want to falback to default view collect serializer retrieval.
    """

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
        This method sanitizes passed errors list.
        This prevents defining Exception Type and same Type instance in errors list.

        Args:
            errors - list of error to be sanitazed

        Returns sanitized errors list.
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
                    f"Exception has been passed multiple times as an instance and as type, \
                        exception type: {type(instance)}"
                )
            else:
                sanitized_errors.append(instance)

        sanitized_errors += types
        return sanitized_errors

    def __init__(
        self,
        collectors: SerializersConfig = None,
        results: SerializersConfig = None,
        errors: List[Union[Exception, Type[Exception]]] = None,
        # NOTE - many is deprecated parameter, it will be removed in future versions
        many: bool = False,
        results_many: bool = False,
        collectors_many: bool = False,
        ignore_view_collectors: bool = False,
        run_get_object: bool = None,
        **kwargs,
    ) -> None:
        self.results_many = results_many or many
        self.collectors_many = collectors_many or many

        self.collectors = collectors or {}
        self.results = results
        self.ignore_view_collectors = ignore_view_collectors

        try:
            self.errors = self._sanitize_error(errors) or []
            self.kwargs = self._sanitize_kwargs(kwargs) or {}
            self.methods = kwargs.get("methods")
            self.framework_decorator = action(**kwargs)
            detail = kwargs.get("detail", False)
            self.run_get_object = (
                run_get_object if run_get_object is not None else detail
            )
            if all(method in SAFE_METHODS for method in self.methods) and collectors:
                raise ImproperlyConfigured(
                    "There should be no collectors defined if there are not create/update requests accepted."
                )
        except ImproperlyConfigured as e:
            if project_settings.DEBUG:
                raise e
            logger.exception("audoma_action has been improperly configured.")

    def _get_error_class(
        self, error: Union[Exception, Type[Exception]]
    ) -> Type[Exception]:
        """
        This is an internal helper method.
        Beacuse we accept errors as instances and classes
        it helps to determine which one is passed.

        Args:
            * error - error object or a class

        Returns: class of passed exception
        """
        if isclass(error):
            return error
        else:
            return type(error)

    def _get_type_matched_exceptions(
        self,
        errors: List[Union[Exception, Type[Exception]]],
        processed_error_class: Type[Exception],
    ) -> List[Union[Exception, Type[Exception]]]:
        """
        This helper function extracts all errors which are
        of the same type as the processed error.
        It simply returns a list of those errors.
        Args:
            errors - list of errors, allowed to be raised in decorated view
            processed_error_class - an exception which has been raised in decorated view

        Returns a List of exceptions and exception classes, with matching exception type.
        """
        type_matched_exceptions = []
        for error in errors:
            error_class = self._get_error_class(error)

            if not processed_error_class == error_class:
                continue

            type_matched_exceptions.append(error)

        return type_matched_exceptions

    def _process_error(
        self,
        raised_error: Union[Exception, Type[Exception]],
        errors: List[Union[Exception, Type[Exception]]],
        view: APIView,
    ) -> None:
        """
        This function processes the raised error.
        It checks if such error should be raised.
        If such error has not been defined/handler is unable to handle it.
        There will be additioanla exception raised or logged, depends on the DEBUG setting.

        Args:
            processed_error - the error which has been raised
            errors - list of errors which may be raised in decorated method
            view - APIView object

        Returns:
            processed_error instance if such error has been defined.
        """
        raised_error_class = self._get_error_class(raised_error)
        error_match = False

        # get all errors with same class as raised exception
        raised_error_response = view.handle_exception(raised_error)
        # In case defined exception handling is not able to handle raised exception,
        # than we simply raise this exception
        if raised_error_response is None:
            view.raise_uncaught_exception(raised_error)

        type_matched_exceptions = self._get_type_matched_exceptions(
            errors, raised_error_class
        )
        for error in type_matched_exceptions:
            if isclass(error):
                error_match = True
                break

            elif all(
                getattr(raised_error_response, attr, None)
                == getattr(view.handle_exception(error), attr, None)
                for attr in ["status_code", "data", "headers"]
            ):
                error_match = True
                break

        if not error_match:
            if project_settings.DEBUG:
                raise AudomaActionException(
                    f"Raised error: {raised_error} has not been \
                        defined in audoma_action errors."
                )

            logger.exception(
                "Error has occured during audoma_action exception processing."
            )

        return raised_error_response

    def _get_collect_serializer_instance(
        self, request: Request, func: Callable, view: APIView
    ) -> BaseSerializer:
        """
        Retrieves collector serializer class and it's config variables.
        Args:
            request - request object
            func - decorated function
            view - view object, which action func belongs to

        Returns:
            Serializer class and it's config variables.

            Config variables:
                partial - says if serializer update should be partial or not.
                view_instance - instance retrieved from view

        """
        collect_serializer = None
        partial = False
        instance = None

        if request.method not in SAFE_METHODS:
            if self.run_get_object:
                instance = view.get_object()

            partial = True if request.method.lower() == "patch" else False

            collect_serializer = view.get_serializer(
                serializer_type="collect",
                instance=instance,
                data=request.data,
                partial=partial,
                context={"request": request, "format": view.format_kwarg, "view": view},
                many=self.collectors_many,
                ignore_view_collectors=self.ignore_view_collectors,
            )

        return collect_serializer

    def _action_return_checks(
        self,
        code: int,
        instance: Union[Iterable, str, APIException, Model],
        response_operation: Union[str, APIException, BaseSerializer],
    ) -> None:
        """
        Perform additional checks for variables returned by view action method.

        Args:
            code - status code of the response, returned as an int
            instance - instance which will be passed to the response serializer
            response_operation - serializer class, APIException or string instance which
                      will be used to create the response

        Returns:
            None
        """

        if code is None:
            raise AudomaActionException(
                "Status code has not been returned to audoma action."
            )

        if not isinstance(response_operation, str) and instance is None:
            raise AudomaActionException(
                "Instance returned in audoma_action decorated \
                    method may not be None if result operation is not str message"
            )

    def __call__(self, func: Callable) -> Callable:
        """ "
        Call of audoma_action decorator.
        This is where the magic happens.

        Args:
            func - decorated function

        Returns:
            wrapper callable.
        """
        func._audoma = AudomaArgs(
            collectors=self.collectors,
            results=self.results,
            errors=self.errors,
            results_many=self.results_many,
            collectors_many=self.collectors_many,
        )
        # apply action decorator
        func = self.framework_decorator(func)

        @wraps(func)
        def wrapper(view: APIView, request: Request, *args, **kwargs) -> Response:
            # extend errors too allow default errors occurance
            errors = deepcopy(func._audoma.errors)
            errors += audoma_settings.COMMON_API_ERRORS + getattr(
                project_settings, "COMMON_API_ERRORS", []
            )
            try:
                collect_serializer = self._get_collect_serializer_instance(
                    request, func, view
                )
                if collect_serializer:
                    collect_serializer.is_valid(raise_exception=True)
                    kwargs["collect_serializer"] = collect_serializer

                instance, code = func(view, request, *args, **kwargs)
                # TODO - add verification

            except Exception as processed_error:
                return self._process_error(processed_error, errors, view)

            response_serializer = view.get_result_serializer(
                instance=instance,
                context={
                    "request": request,
                    "format": view.format_kwarg,
                    "view": view,
                },
                many=self.results_many,
                status_code=code,
            )

            if hasattr(view, "_retrieve_response_headers"):
                headers = view._retrieve_response_headers(code, response_serializer)
            else:
                headers = {}

            return Response(
                response_serializer.data,
                status=code,
                headers=headers,
            )

        return wrapper
