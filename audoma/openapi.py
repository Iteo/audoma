from __future__ import annotations

import typing

from django.utils.translation import gettext_lazy as _
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import error
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from audoma.drf.docs.inspectors import MultiSerializersMixin
from audoma.drf.docs.inspectors import PermissionDescriptionMixin
from audoma.drf.generics import GenericAPIView as AudomaGenericAPIView


class AudomaAutoSchema(AutoSchema):

    def _get_serializer(self, serializer_type='collect'):
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
