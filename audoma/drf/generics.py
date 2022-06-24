from typing import Type

from rest_framework import generics
from rest_framework.serializers import BaseSerializer


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
        serializer_class = kwargs.pop(
            "serializer_class",
            self.get_serializer_class(type=serializer_type, many=many),
        )
        kwargs["context"] = self.get_serializer_context()

        return serializer_class(*args, **kwargs)

    # needed by AudomaSwaggerAutoSchema
    def get_result_serializer(self, *args, **kwargs) -> BaseSerializer:
        """
        Shortuct for get_serializer.
        Simply has serializer_type set to `result`
        """
        return self.get_serializer(*args, serializer_type="result", **kwargs)

    def get_serializer_class(
        self, type: str = "collect", many: bool = False
    ) -> Type[BaseSerializer]:
        """
        Extends defuault `get_serializer_class` method.
        This returns proper serializer_class for current request.

        Args:
            type - type of serializer to be returned, it may be collect or result serializer.

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
        method = self.request.method.lower()
        if self.action == "metadata":
            action = self.action_map.get("post", "list")
        else:
            action = self.action
        attr_names = [
            "%s_%s_%s_serializer_class" % (method, action, type),
            "%s_%s_serializer_class" % (action, type),
            "%s_%s_serializer_class" % (method, action),
            "%s_serializer_class" % (action),
            "common_%s_serializer_class" % (type),
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
            "or override the `get_serializer_class()` method." % self.__class__.__name__
        )

        if (
            type == "result"
            and self.action != "list"
            and hasattr(serializer_class, "get_result_serializer_class")
        ):
            assert callable(serializer_class.get_result_serializer_class)
            serializer_class = serializer_class.get_result_serializer_class(many=many)

        return serializer_class
