from __future__ import annotations

import typing

from drf_spectacular.drainage import get_override
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import (
    build_examples_list,
    error,
    force_instance,
    sanitize_specification_extensions,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework.generics import GenericAPIView
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from audoma.drf.generics import GenericAPIView as AudomaGenericAPIView
from audoma.drf.validators import ExclusiveFieldsValidator
from audoma.openapi_helpers import (
    build_exclusive_fields_examples,
    build_exclusive_fields_schema,
    get_permissions_description,
)


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

    def _get_examples(
        self,
        serializer,
        direction: str,
        media_type: str,
        status_code: str = None,
        extras: list = None,
    ) -> typing.List[dict]:
        examples = super()._get_examples(
            serializer, direction, media_type, status_code, extras
        )
        if not hasattr(serializer, "validators") or direction == "response":
            return examples

        examples = []
        for validator in serializer.validators:
            if isinstance(validator, ExclusiveFieldsValidator):
                examples += build_exclusive_fields_examples(
                    serializer, validator.fields, examples
                )
        if examples:
            examples = build_examples_list(examples)
        return examples

    def _map_serializer(
        self,
        serializer: typing.Union[
            OpenApiTypes, BaseSerializer, typing.Type[BaseSerializer]
        ],
        direction: str,
        bypass_extensions: bool = False,
    ) -> dict:
        serializer = force_instance(serializer)
        serializer_extension = OpenApiSerializerExtension.get_match(serializer)

        if serializer_extension and not bypass_extensions:
            schema = serializer_extension.map_serializer(self, direction)
        else:
            schema = self._map_basic_serializer(serializer, direction)

        if hasattr(serializer, "validators") and direction == "request":
            subschemas = []
            for validator in serializer.validators:
                if isinstance(validator, ExclusiveFieldsValidator):
                    subschemas += build_exclusive_fields_schema(
                        schema, validator.fields
                    )

            if subschemas:
                schema = {"oneOf": subschemas}

        extensions = get_override(serializer, "extensions", {})
        if extensions:
            schema.update(sanitize_specification_extensions(extensions))

        return self._postprocess_serializer_schema(schema, serializer, direction)
