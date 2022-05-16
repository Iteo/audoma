from __future__ import annotations

import typing

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import (
    error,
    force_instance,
)
from rest_framework.fields import Field
from rest_framework.generics import GenericAPIView
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from audoma.drf.generics import GenericAPIView as AudomaGenericAPIView
from audoma.links import (
    ChoicesOptionsLink,
    ChoicesOptionsLinkSchemaGenerator,
)
from audoma.openapi_helpers import (
    AudomaApiResponseCreator,
    get_permissions_description,
)


class AudomaAutoSchema(AutoSchema):

    choice_link_schema_generator = ChoicesOptionsLinkSchemaGenerator()
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
                method_serializers = action_serializers[method.lower()]
                for key in action_serializers:
                    if isinstance(key, int):
                        method_serializers[key] = action_serializers[key]
                return method_serializers
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
            field, direction, bypass_extensions=bypass_extensions
        )
        if hasattr(field, "choices"):
            result["x-choices"] = self._get_enum_choices_for_field(field)

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
