from unittest import TestCase

from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
)

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


class AudomaAutoSchemaTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_get_description_no_permissions_success(self):
        class ExampleView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
            """
            Test View Doc
            """

            permission_classes = []

        view = ExampleView()
        view.schema = AudomaAutoSchema()
        view.schema.method = "get"
        desc = view.schema.get_description()
        self.assertEqual(desc, """Test View Doc""")

    def test_get_description_with_basic_permissions_success(self):
        class ExampleView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
            """
            Test View Doc
            """

        view = ExampleView()
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

        class ExampleView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
            """
            Test View Doc
            """

            permission_classes = [ExampleCustomPermission & IsAuthenticated]

        view = ExampleView()
        view.schema = AudomaAutoSchema()
        view.schema.method = "get"
        desc = view.schema.get_description()
        self.assertIn("`ExampleCustomPermission`  &  `IsAuthenticated`", desc)
        self.assertIn("Test View Doc", desc)
