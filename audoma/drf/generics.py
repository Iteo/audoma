from typing import (
    Callable,
    Type,
)

from rest_framework import generics
from rest_framework.settings import api_settings

from audoma.decorators import AudomaArgs
from audoma.drf.serializers import (
    BaseSerializer,
    DefaultMessageSerializer,
)
from audoma.operations import OperationExtractor


LOCATION_HEADER_STATUSES = [201] + list(range(300, 400))


class GenericAPIView(generics.GenericAPIView):

    """
    Extended GenericAPIView known from rest_framework.
    This class extends `get_serializer` and `get_serializer_class` methods.
    Also provides `get_result_serializer`, which is a shourtcut for `get_serializer` with proper param.
    """

    def get_serializer(self, *args, **kwargs) -> BaseSerializer:
        """
        Passes additional param to `get_serializer_class`.

        kwargs:
            serializer_type - defines if serializer is collect or result serializer.
                result serializer will be used to produce response, collect to process incoming data.
            serializer_class - it is possible to pass serializer_class to get_serializer, this will
                ends with returning passed serializer_class object.

        Returns:
            Object of obtained serializer class.
        """
        many = kwargs.get("many", False)

        serializer_type = kwargs.pop("serializer_type", "collect")
        status_code = kwargs.pop("status_code", None)
        audoma_action_serializer_only = kwargs.pop("ignore_view_collectors", False)
        serializer_class = kwargs.pop(
            "serializer_class",
            self.get_serializer_class(
                serializer_type=serializer_type,
                many=many,
                status_code=status_code,
                audoma_action_serializer_only=audoma_action_serializer_only,
            ),
        )
        # this is possible for audoma_action
        if not serializer_class:
            return None

        kwargs["context"] = self.get_serializer_context()

        if (
            kwargs.get("instance") is None
            and serializer_class is DefaultMessageSerializer
        ):
            audoma_args = self.get_audoma_action_config()
            message = self._extract_audoma_action_serializer(
                serializer_type, audoma_args, status_code
            )
            kwargs["instance"] = {"message": message}

        return serializer_class(*args, **kwargs)

    # needed by AudomaSwaggerAutoSchema
    def get_result_serializer(self, *args, **kwargs) -> BaseSerializer:
        """
        Shortuct for get_serializer.
        Simply has serializer_type set to `result`
        """
        return self.get_serializer(*args, serializer_type="result", **kwargs)

    def _check_action_function(self):
        func = getattr(self, self.action, None)
        if func and callable(func):
            return hasattr(func, "_audoma")
        return False

    def _extract_audoma_action_serializer(
        self, serializer_type: str, audoma_args: AudomaArgs, status_code: int = None
    ):

        extractor = OperationExtractor(
            audoma_args.collectors, audoma_args.results, audoma_args.errors
        )
        operation_category = "response" if serializer_type == "result" else "collect"

        # TODO - consider this idea
        if not status_code and operation_category == "response":
            return None

        return extractor.extract_operation(
            self.request, status_code, operation_category
        )

    def get_audoma_action_config(self):
        audoma_args = None
        if self._check_action_function():
            func = getattr(self, self.action)
            audoma_args = getattr(func, "_audoma", None)
        return audoma_args

    def get_audoma_action_serializer_class(
        self, serializer_type: str, status_code: int = None
    ):
        audoma_args = self.get_audoma_action_config()
        if audoma_args is None:
            return None

        serializer_class = self._extract_audoma_action_serializer(
            serializer_type, audoma_args, status_code
        )

        if isinstance(serializer_class, str):
            serializer_class = DefaultMessageSerializer

        return serializer_class

    def get_serializer_class(
        self,
        serializer_type: str = "collect",
        many: bool = False,
        status_code: int = None,
        audoma_action_serializer_only: bool = False,
    ) -> Type[BaseSerializer]:
        """
        Extends defuault `get_serializer_class` method.
        This returns proper serializer_class for current request.

        Args:
            serializer_type - serializer_type of serializer to be returned, it may be collect or result serializer.

        Returns:
            This returns serializer_class

        """
        assert self.action not in [
            "post",
            "put",
            "delete",
            "patch",
            "options",
            "get",
            "head",
        ]
        serializer_class = self.get_audoma_action_serializer_class(
            serializer_type, status_code
        )
        if audoma_action_serializer_only:
            return serializer_class

        if not serializer_class:
            method = self.request.method.lower()
            if self.action == "metadata":
                action = self.action_map.get("post", "list")
            else:
                action = self.action
            attr_names = [
                "%s_%s_%s_serializer_class" % (method, action, serializer_type),
                "%s_%s_serializer_class" % (action, serializer_type),
                "%s_%s_serializer_class" % (method, action),
                "%s_serializer_class" % (action),
                "common_%s_serializer_class" % (serializer_type),
                "serializer_class",
            ]
            for attr_name in attr_names:
                try:
                    serializer_class = getattr(self, attr_name)
                except AttributeError:
                    continue
                else:
                    break

            assert serializer_class is not None, (
                "'%s' should either include a `serializer_class`  attribute, "
                "or override the `get_serializer_class()` method."
                % self.__class__.__name__
            )

        if (
            serializer_type == "result"
            and self.action != "list"
            and hasattr(serializer_class, "get_result_serializer_class")
        ):
            assert callable(serializer_class.get_result_serializer_class)
            serializer_class = serializer_class.get_result_serializer_class()

        return serializer_class

    def _retrieve_response_headers(
        self,
        status_code: int,
        result_serializer: BaseSerializer,
    ):
        method = self.request.method.lower()

        method_names = [
            f"get_{self.action}_{self.request.method.lower()}_response_headers",
            f"get_{self.action}_response_headers",
            f"get_{self.request.method}_response_headers",
            "get_response_headers",
        ]
        headers = {}
        for name in method_names:
            method = getattr(self, name, None)
            if not method or not isinstance(method, Callable):
                continue
            headers = method(result_serializer)
            break

        # Append Location header for status proper status codes automatically.
        # For more info check:
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Location
        if status_code in LOCATION_HEADER_STATUSES:
            data = result_serializer.data
            try:
                if "Location" not in headers:
                    headers["Location"] = str(data[api_settings.URL_FIELD_NAME])
            except KeyError:
                pass
        return headers
