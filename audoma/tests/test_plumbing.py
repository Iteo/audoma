from unittest import TestCase

from rest_framework import (
    generics,
    mixins,
    serializers,
    views,
    viewsets,
)

from audoma.drf import (
    generics as audoma_generics,
    mixins as audoma_mixins,
    serializers as audoma_serializers,
    viewsets as audoma_viewsets,
)
from audoma.plumbing import (
    create_choices_enum_description,
    get_lib_doc_excludes_audoma,
)


class PlumbingTestCase(TestCase):
    def setUp(self):
        super().setUp()

    def test_create_choices_enum_description_dict_choices(self):
        description = create_choices_enum_description(
            {1: "One", 2: "Two", 3: "Three"}, "example_field"
        )
        self.assertEqual(
            description,
            "Filter by example_field \n * `1` - One\n * `2` - Two\n * `3` - Three\n",
        )

    def test_create_choices_enum_description_non_dict_choices(self):
        description = create_choices_enum_description(
            [(1, "One"), (2, "Two"), (3, "Three")], "example_field"
        )
        self.assertEqual(
            description,
            "Filter by example_field \n * `1` - One\n * `2` - Two\n * `3` - Three\n",
        )

    def test_get_lib_doc_excludes_audoma(self):
        expected_exclude_list = [
            views.APIView,
            serializers.BaseSerializer,
            serializers.HyperlinkedModelSerializer,
            serializers.ListSerializer,
            serializers.ModelSerializer,
            serializers.Serializer,
            viewsets.GenericViewSet,
            viewsets.ModelViewSet,
            viewsets.ReadOnlyModelViewSet,
            viewsets.ViewSet,
            generics.CreateAPIView,
            generics.DestroyAPIView,
            generics.GenericAPIView,
            generics.ListAPIView,
            generics.ListCreateAPIView,
            generics.RetrieveAPIView,
            generics.RetrieveDestroyAPIView,
            generics.RetrieveUpdateAPIView,
            generics.RetrieveUpdateDestroyAPIView,
            generics.UpdateAPIView,
            mixins.CreateModelMixin,
            mixins.DestroyModelMixin,
            mixins.ListModelMixin,
            mixins.RetrieveModelMixin,
            mixins.UpdateModelMixin,
            audoma_viewsets.GenericViewSet,
            audoma_mixins.ActionModelMixin,
            audoma_mixins.BulkCreateModelMixin,
            audoma_mixins.BulkUpdateModelMixin,
            audoma_mixins.CreateModelMixin,
            audoma_mixins.DestroyModelMixin,
            audoma_mixins.ListModelMixin,
            audoma_mixins.RetrieveModelMixin,
            audoma_mixins.UpdateModelMixin,
            audoma_serializers.BaseSerializer,
            audoma_serializers.BulkListSerializer,
            audoma_serializers.DefaultMessageSerializer,
            audoma_serializers.HyperlinkedModelSerializer,
            audoma_serializers.ListSerializer,
            audoma_serializers.ModelSerializer,
            audoma_serializers.Serializer,
            audoma_generics.GenericAPIView,
        ]
        exclude_list = get_lib_doc_excludes_audoma()
        self.assertEqual(exclude_list, expected_exclude_list)
