from __future__ import annotations
from drf_spectacular.openapi import AutoSchema
from rest_framework.generics import CreateAPIView, GenericAPIView, ListCreateAPIView
from rest_framework.views import APIView
import typing

from drf_spectacular.plumbing import error, build_parameter_type
import copy
import re
import typing
from collections import defaultdict

import uritemplate
from django.core import exceptions as django_exceptions
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, renderers, serializers
from rest_framework.fields import _UnvalidatedField, empty
from rest_framework.generics import CreateAPIView, GenericAPIView, ListCreateAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.schemas.inspectors import ViewInspector
from rest_framework.schemas.utils import get_pk_description  # type: ignore
from rest_framework.settings import api_settings
from rest_framework.utils.model_meta import get_field_info
from rest_framework.views import APIView

from drf_spectacular.authentication import OpenApiAuthenticationExtension
from drf_spectacular.contrib import *  # noqa: F403, F401
from drf_spectacular.drainage import add_trace_message, get_override, has_override
from drf_spectacular.extensions import (
    OpenApiFilterExtension, OpenApiSerializerExtension, OpenApiSerializerFieldExtension,
)
from drf_spectacular.plumbing import (
    ComponentRegistry, ResolvedComponent, UnableToProceedError, append_meta,
    assert_basic_serializer, build_array_type, build_basic_type, build_choice_field,
    build_examples_list, build_generic_type, build_media_type_object, build_object_type,
    build_parameter_type, error, follow_field_source, follow_model_field_lookup, force_instance,
    get_doc, get_type_hints, get_view_model, is_basic_serializer, is_basic_type, is_field,
    is_list_serializer, is_patched_serializer, is_serializer, is_trivial_string_variation,
    modify_media_types_for_versioning, resolve_django_path_parameter, resolve_regex_path_parameter,
    resolve_type_hint, safe_ref, sanitize_specification_extensions, warn, whitelisted,
)
from drf_spectacular.settings import spectacular_settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse
from audoma.drf.generics import GenericAPIView as AudomaGenericAPIView


class AudomaAutoSchema(AutoSchema):

    # przyjmowac parametr - domyslenie collect
    def _get_serializer(self, serializer_type=None):
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
                if callable(getattr(view, 'get_serializer', None)):
                    return view.get_serializer()
                elif callable(getattr(view, 'get_serializer_class', None)):
                    return view.get_serializer_class()()
                elif hasattr(view, 'serializer_class'):
                    return view.serializer_class
                else:
                    error(
                        'unable to guess serializer. This is graceful '
                        'fallback handling for APIViews. Consider using GenericAPIView as view base '
                        'class, if view is under your control. Ignoring view for now. '
                    )
            else:
                error('Encountered unknown view base class. Please report this issue. Ignoring for now')
        except Exception as exc:
            error(
                f'exception raised while getting serializer. Hint: '
                f'Is get_serializer_class() returning None or is get_queryset() not working without '
                f'a request? Ignoring the view for now. (Exception: {exc})'
            )

    def get_request_serializer(self) -> typing.Any:
        """ override this for custom behaviour """
        return self._get_serializer()

    def get_response_serializers(self) -> typing.Any:
        """ override this for custom behaviour """
        return self._get_serializer(serializer_type='result')

    def _map_serializer_field(self, field, direction, bypass_extensions=False):
        has_annotation = hasattr(
            field, '_spectacular_annotation') and 'field' in field._spectacular_annotation and isinstance(field._spectacular_annotation['field'], dict)
        if has_annotation:
            annotation = field._spectacular_annotation
            field._spectacular_annotation = {}

        result = super()._map_serializer_field(field, direction, bypass_extensions=False)
        if has_annotation:
            result.update(annotation['field'])
        return result
