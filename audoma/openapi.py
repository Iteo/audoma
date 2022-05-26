from __future__ import annotations

import typing

from drf_spectacular.drainage import get_override
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import (
    build_array_type,
    build_examples_list,
    error,
    force_instance,
    sanitize_specification_extensions,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework.fields import Field
from rest_framework.generics import GenericAPIView
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from audoma.drf.generics import GenericAPIView as AudomaGenericAPIView
from audoma.drf.serializers import BulkSerializerMixin
from audoma.drf.validators import ExclusiveFieldsValidator
from audoma.openapi_helpers import (
    AudomaApiResponseCreator,
    build_exclusive_fields_examples,
    build_exclusive_fields_schema,
    get_permissions_description,
)


class AudomaAutoSchema(AutoSchema):
    response_creator = AudomaApiResponseCreator()

    def get_description(self) -> str:
        view = self.view
        description = super().get_description() or ""
        description += get_permissions_description(view)
        return description

    def _get_serializer(  # noqa: C901
        self, serializer_type="collect"
    ) -> typing.Union[BaseSerializer, typing.Type[BaseSerializer]]:
        view = self.view
        method = view.request.method

        # code responsible for documenting AudomaAction decorator
        if serializer_type == "collect":
            action_serializers = self.response_creator.extract_collectors(view)
        else:
            action_serializers = self.response_creator.extract_results(view)

        if action_serializers:
            if (
                isinstance(action_serializers, dict)
                and method.lower() in action_serializers
            ):
                return action_serializers[method.lower()]
            else:
                return action_serializers

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

    def get_response_serializers(
        self,
    ) -> typing.Union[BaseSerializer, typing.Type[BaseSerializer]]:
        """overrides this for custom behaviour"""
        return self._get_serializer(serializer_type="result")

    def _map_serializer_field(
        self, field: Field, direction: str, bypass_extensions=False
    ) -> dict:
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

        schema_resp = super()._get_response_for_code(
            serializer, status_code, media_types
        )

        if isinstance(serializer, BulkSerializerMixin) and self.view.action != "list":
            for media_type in schema_resp["content"]:
                schema = schema_resp["content"][media_type]["schema"]
                schema_resp["content"][media_type]["schema"] = {
                    "oneOf": [build_array_type(schema), schema]
                }

        return schema_resp

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

        serializer = force_instance(serializer)
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
