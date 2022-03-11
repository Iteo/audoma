from rest_framework import generics


class GenericAPIView(generics.GenericAPIView):
    def get_serializer(self, *args, **kwargs):
        serializer_type = kwargs.pop("serializer_type", "collect")
        serializer_class = kwargs.pop(
            "serializer_class", self.get_serializer_class(type=serializer_type)
        )
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    # needed by AudomaSwaggerAutoSchema
    def get_result_serializer(self, *args, **kwargs):
        return self.get_serializer(*args, serializer_type="result", **kwargs)

    def get_serializer_class(self, type="collect"):
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
            serializer_class = serializer_class.get_result_serializer_class()

        return serializer_class
