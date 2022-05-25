from __future__ import annotations

import typing

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import (
    error,
    force_instance,
)
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from audoma.drf.generics import GenericAPIView as AudomaGenericAPIView
from audoma.links import (
    ChoicesOptionsLink,
    ChoicesOptionsLinkSchemaGenerator,
)
from audoma.openapi_helpers import get_permissions_description
from audoma.plumbing import create_choices_enum_description


class AudomaAutoSchema(AutoSchema):

    choice_link_schema_generator = ChoicesOptionsLinkSchemaGenerator()

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

    def _get_enum_choices_for_field(self, field):
        if hasattr(field, "original_choices"):
            choices = field.original_choices
        else:
            choices = field.choices
        return {"choices": {key: value for key, value in choices}}

    def _get_link_choices_for_field(self, field, serializer):
        link = serializer.choices_options_links.get(field.field_name, None)
        if not link:
            return

        if isinstance(link, dict):
            # presume that this dictionary are link kwargs
            link.update(
                {"field_name": field.field_name, "serializer_class": type(serializer)}
            )
            link = ChoicesOptionsLink(**link)

        choices = self.choice_link_schema_generator.generate_schema(link)
        if choices:
            if link.field_name == field.field_name:
                return choices
        return

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
            field, direction, bypass_extensions=bypass_extensions
        )
        if hasattr(field, "choices"):
            result["x-choices"] = self._get_enum_choices_for_field(field)
            result["description"] = create_choices_enum_description(
                result["x-choices"]["choices"], field.field_name
            )

        serializer_type = "collect" if direction == "request" else "result"
        serializer = self._get_serializer(serializer_type=serializer_type)
        serializer = force_instance(serializer)

        if hasattr(serializer, "choices_options_links"):
            choices = self._get_link_choices_for_field(field, serializer)
            if choices:
                result["x-choices"] = choices

        if has_annotation:
            result.update(annotation["field"])
        return result
