from rest_framework import generics, views, viewsets, mixins, serializers
from drf_spectacular.drainage import cache
from audoma.drf import viewsets as audoma_viewsets
from audoma.drf import mixins as audoma_mixins
from audoma.drf import generics as audoma_generics
from audoma.drf import serializers as audoma_serializers


@cache
def get_lib_doc_excludes_audoma():

    return [
        views.APIView,
        *[getattr(serializers, c) for c in dir(serializers) if c.endswith('Serializer')],
        *[getattr(viewsets, c) for c in dir(viewsets) if c.endswith('ViewSet')],
        *[getattr(generics, c) for c in dir(generics) if c.endswith('APIView')],
        *[getattr(mixins, c) for c in dir(mixins) if c.endswith('Mixin')],
        *[getattr(audoma_viewsets, c) for c in dir(audoma_viewsets) if c.endswith('ViewSet')],
        *[getattr(audoma_mixins, c) for c in dir(audoma_mixins) if c.endswith('Mixin')],
        *[getattr(audoma_serializers, c) for c in dir(audoma_serializers) if c.endswith('Serializer')],
        *[getattr(audoma_generics, c) for c in dir(audoma_generics) if c.endswith('APIView')],
    ]
