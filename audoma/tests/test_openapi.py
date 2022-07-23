from unittest import TestCase

from rest_framework import fields
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
)
from rest_framework.serializers import Serializer
from rest_framework.test import APIRequestFactory

from audoma.drf.mixins import (
    ActionModelMixin,
    BulkCreateModelMixin,
    BulkUpdateModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from audoma.drf.viewsets import GenericViewSet
from audoma.openapi import AudomaAutoSchema
from audoma.tests.testtools import (
    create_serializer,
    create_serializer_class,
    create_view,
)


class AudomaAutoSchemaTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.factory = APIRequestFactory()

    def test_get_description_no_permissions_success(self):
        view = create_view(view_properties={"permission_classes": []})
        view.schema = AudomaAutoSchema()
        view.schema.method = "get"
        desc = view.schema.get_description()
        self.assertEqual(desc, """Test View Doc""")

    def test_get_description_with_basic_permissions_success(self):
        view = create_view()
        view.schema = AudomaAutoSchema()
        view.schema.method = "get"
        desc = view.schema.get_description()
        self.assertIn("**Permissions:**", desc)
        self.assertIn("Test View Doc", desc)
        self.assertIn("`AllowAny`", desc)

    def test_get_description_with_custom_permission_success(self):
        class ExampleCustomPermission(BasePermission):
            """
            Some Custom Permission
            """

            def has_permission(self, requst, view):
                ...

        permission_classes = [ExampleCustomPermission & IsAuthenticated]
        view = create_view(view_properties={"permission_classes": permission_classes})
        view.schema = AudomaAutoSchema()
        view.schema.method = "get"
        desc = view.schema.get_description()
        self.assertIn("`ExampleCustomPermission`  &  `IsAuthenticated`", desc)
        self.assertIn("Test View Doc", desc)

    def test_get_description_no_description_permission_success(self):
        class SomePermission(BasePermission):
            ...

        permission_classes = [SomePermission]
        view = create_view(view_properties={"permission_classes": permission_classes})
        view.schema = AudomaAutoSchema()
        view.schema.method = "get"
        desc = view.schema.get_description()
        self.assertIn("(No description for this permission)", desc)

    def test_get_serializer_default_serializer_usage(self):
        fields_config = {
            "name": fields.CharField(max_length=255),
            "age": fields.IntegerField(),
        }

        serializer_class = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )
        view = create_view(view_properties={"serializer_class": serializer_class})
        view.schema = AudomaAutoSchema()
        view.request = self.factory.get("/example/")
        view.action = "retrieve"
        serializer = view.schema._get_serializer()
        self.assertEqual(serializer_class, type(serializer))

    def test_get_serializer_collect_serializer_class_success(self):
        fields_config = {
            "name": fields.CharField(max_length=255),
            "age": fields.IntegerField(),
        }

        serializer_class = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )
        view = create_view(
            view_properties={"common_collect_serializer_class": serializer_class}
        )
        view.schema = AudomaAutoSchema()
        view.request = self.factory.get("/example/")
        view.action = "retrieve"
        serializer = view.schema._get_serializer()
        self.assertEqual(serializer_class, type(serializer))

    def test_get_serializer_result_serializer_class_success(self):
        fields_config = {
            "name": fields.CharField(max_length=255),
            "age": fields.IntegerField(),
        }

        serializer_class = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )
        view = create_view(
            view_properties={"common_result_serializer_class": serializer_class}
        )
        view.schema = AudomaAutoSchema()
        view.request = self.factory.get("/example/")
        view.action = "retrieve"
        serializer = view.schema._get_serializer(serializer_type="result")
        self.assertEqual(serializer_class, type(serializer))

    def test_get_serializer_retrieve_serializer_class_success(self):
        fields_config = {
            "name": fields.CharField(max_length=255),
            "age": fields.IntegerField(),
        }

        serializer_class = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )
        view = create_view(
            view_properties={"retrieve_serializer_class": serializer_class}
        )
        view.schema = AudomaAutoSchema()
        view.request = self.factory.get("/example/")
        view.action = "retrieve"
        serializer = view.schema._get_serializer(serializer_type="result")
        self.assertEqual(serializer_class, type(serializer))

    def test_get_serializer_get_retrieve_serializer_class_success(self):
        fields_config = {
            "name": fields.CharField(max_length=255),
            "age": fields.IntegerField(),
        }

        serializer_class = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )
        view = create_view(
            view_properties={"get_retrieve_serializer_class": serializer_class}
        )
        view.schema = AudomaAutoSchema()
        view.request = self.factory.get("/example/")
        view.action = "retrieve"
        serializer = view.schema._get_serializer(serializer_type="result")
        self.assertEqual(serializer_class, type(serializer))

    def test_get_serializer_get_retrieve_result_serializer_class_success(self):
        fields_config = {
            "name": fields.CharField(max_length=255),
            "age": fields.IntegerField(),
        }

        serializer_class = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )
        view = create_view(
            view_properties={"get_retrieve_result_serializer_class": serializer_class}
        )
        view.schema = AudomaAutoSchema()
        view.request = self.factory.get("/example/")
        view.action = "retrieve"
        serializer = view.schema._get_serializer(serializer_type="result")
        self.assertEqual(serializer_class, type(serializer))

    def test_get_serializer_no_serializer_class_failure(self):
        view = create_view(view_properties={"serializer_class": None})
        view.schema = AudomaAutoSchema()
        view.request = self.factory.get("/example/")
        view.action = "retrieve"
        serializer = view.schema._get_serializer(serializer_type="result")
        self.assertIsNone(serializer)

    def test_get_serializer_class_audoma_action_success(self):
        ...
