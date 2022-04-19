from __future__ import annotations

import typing
from inspect import isclass

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import error
from rest_framework.generics import GenericAPIView
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from audoma.drf.generics import GenericAPIView as AudomaGenericAPIView
from audoma.links import AudomaOptionsLinkSchemaGenerator
from audoma.openapi_helpers import get_permissions_description


class AudomaAutoSchema(AutoSchema):
    def get_description(self):
        view = self.view
        description = super().get_description() or ""
        description += get_permissions_description(view)
        return description

    def _add_link_to_response_schema(
        self, schema: dict, serializer: BaseSerializer, status_code: str
    ):
        generator = AudomaOptionsLinkSchemaGenerator(serializer)
        links_schema = generator.generate_schema()
        schema[status_code]["links"] = links_schema
        return schema

    def _get_response_bodies(self):
        schema = super()._get_response_bodies()

        serializer = self._get_serializer(serializer_type="result")
        if not (isinstance(serializer, BaseSerializer) or isinstance(serializer, dict)):
            return schema
        if isinstance(serializer, BaseSerializer):
            # get serializer instance
            if isclass(serializer):
                serializer = serializer()
            schema = self._add_link_to_response_schema(
                schema, serializer, list(schema.keys())[0]
            )
        elif isinstance(serializer, dict):
            serializers = serializer
            for key, serializer in serializers:
                if isclass(serializer):
                    serializer = serializer()
                schema = self._add_link_to_response_schema(schema, serializer, key)

        return schema

    def _get_serializer(self, serializer_type="collect"):  # noqa: C901
        view = self.view
        try:
            if isinstance(view, AudomaGenericAPIView):
                if view.__class__.get_serializer == AudomaGenericAPIView.get_serializer:
                    return view.get_serializer_class(type=serializer_type)()
                return view.get_serializer()
            elif isinstance(view, GenericAPIView):
                # try to circumvent queryset issues with calling get_serializer. if view has NOT
                # overridden get_serializer, its safe to use get_serializer_class.
                if view.__class__.get_serializer == GenericAPIView.get_serializer:
                    return view.get_serializer_class()()
                return view.get_serializer()
            elif isinstance(view, APIView):
                # APIView does not implement the required interface, but be lenient and make
                # good guesses before giving up and emitting a warning.
                if callable(getattr(view, "get_serializer", None)):
                    return view.get_serializer()
                elif callable(getattr(view, "get_serializer_class", None)):
                    return view.get_serializer_class()()
                elif hasattr(view, "serializer_class"):
                    return view.serializer_class
                else:
                    error(
                        "unable to guess serializer. This is graceful "
                        "fallback handling for APIViews. Consider using GenericAPIView as view base "
                        "class, if view is under your control. Ignoring view for now. "
                    )
            else:
                error(
                    "Encountered unknown view base class. Please report this issue. Ignoring for now"
                )
        except Exception as exc:
            error(
                f"exception raised while getting serializer. Hint: "
                f"Is get_serializer_class() returning None or is get_queryset() not working without "
                f"a request? Ignoring the view for now. (Exception: {exc})"
            )

    def get_response_serializers(self) -> typing.Any:
        """overrides this for custom behaviour"""
        return self._get_serializer(serializer_type="result")

    def _map_serializer_field(self, field, direction, bypass_extensions=False):
        """
        Allows to use @extend_schema_field with `field` dict so that
        it gets updated instead of being overriden
        """
        has_annotation = (
            hasattr(field, "_spectacular_annotation")
            and "field" in field._spectacular_annotation
            and isinstance(field._spectacular_annotation["field"], dict)
        )
        if has_annotation:
            annotation = field._spectacular_annotation
            field._spectacular_annotation = {}

        result = super()._map_serializer_field(
            field, direction, bypass_extensions=False
        )
        if has_annotation:
            result.update(annotation["field"])
        return result
