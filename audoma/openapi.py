from __future__ import annotations

import typing

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import (
    build_array_type,
    build_media_type_object,
    error,
    force_instance,
    modify_media_types_for_versioning,
)
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from django.utils.translation import gettext_lazy as _

from audoma.drf.generics import GenericAPIView as AudomaGenericAPIView
from audoma.drf.serializers import BulkSerializerMixin
from audoma.openapi_helpers import get_permissions_description


class AudomaAutoSchema(AutoSchema):
    def get_description(self):
        view = self.view
        description = super().get_description() or ""
        description += get_permissions_description(view)
        return description

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

    def _get_request_for_media_type(self, serializer):

        schema, request_body_required = super()._get_request_for_media_type(serializer)

        if isinstance(serializer, BulkSerializerMixin) and self.view.action != "list":
            schema = {"oneOf": [build_array_type(schema), schema]}
        return schema, request_body_required

    def _get_response_for_code(self, serializer, status_code, media_types=None):

        if isinstance(serializer, BulkSerializerMixin) and self.view.action != "list":
            description, examples = "", []

            serializer = force_instance(serializer)
            headers = self._get_response_headers_for_code(status_code)
            headers = {"headers": headers} if headers else {}

            component = self.resolve_serializer(serializer, "response")

            schema = {"oneOf": [build_array_type(component.ref), component.ref]}

            if not media_types:
                media_types = self.map_renderers("media_type")

            media_types = modify_media_types_for_versioning(self.view, media_types)

            return {
                **headers,
                "content": {
                    media_type: build_media_type_object(
                        schema,
                        self._get_examples(
                            serializer, "response", media_type, status_code, examples
                        ),
                    )
                    for media_type in media_types
                },
                "description": description,
            }

        return super()._get_response_for_code(serializer, status_code, media_types)
