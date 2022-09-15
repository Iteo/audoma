from unittest import TestCase

from drf_spectacular.plumbing import ComponentRegistry
from rest_framework import fields
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
)
from rest_framework.serializers import Serializer
from rest_framework.test import APIRequestFactory

from audoma.drf import (
    fields as audoma_fields,
    serializers as audoma_serializers,
)
from audoma.drf.validators import ExclusiveFieldsValidator
from audoma.openapi import AudomaAutoSchema
from audoma.tests.testtools import (
    create_basic_view,
    create_serializer,
    create_serializer_class,
    create_view_with_custom_action,
    create_view_with_custom_audoma_action,
)


class AudomaAutoSchemaTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.factory = APIRequestFactory()

    def test_get_description_no_permissions_success(self):
        view = create_basic_view(view_properties={"permission_classes": []})
        view.schema = AudomaAutoSchema()
        view.schema.method = "get"
        desc = view.schema.get_description()
        self.assertEqual(desc, """Test View Doc""")

    def test_get_description_with_basic_permissions_success(self):
        view = create_basic_view()
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
        view = create_basic_view(
            view_properties={"permission_classes": permission_classes}
        )
        view.schema = AudomaAutoSchema()
        view.schema.method = "get"
        desc = view.schema.get_description()
        self.assertIn("`ExampleCustomPermission`  &  `IsAuthenticated`", desc)
        self.assertIn("Test View Doc", desc)

    def test_get_description_no_description_permission_success(self):
        class SomePermission(BasePermission):
            ...

        permission_classes = [SomePermission]
        view = create_basic_view(
            view_properties={"permission_classes": permission_classes}
        )
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
        view = create_basic_view(view_properties={"serializer_class": serializer_class})
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
        view = create_basic_view(
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
        view = create_basic_view(
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
        view = create_basic_view(
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
        view = create_basic_view(
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
        view = create_basic_view(
            view_properties={"get_retrieve_result_serializer_class": serializer_class}
        )
        view.schema = AudomaAutoSchema()
        view.request = self.factory.get("/example/")
        view.action = "retrieve"
        serializer = view.schema._get_serializer(serializer_type="result")
        self.assertEqual(serializer_class, type(serializer))

    def test_get_serializer_no_serializer_class_failure(self):
        view = create_basic_view(view_properties={"serializer_class": None})
        view.schema = AudomaAutoSchema()
        view.request = self.factory.get("/example/")
        view.action = "retrieve"
        serializer = view.schema._get_serializer(serializer_type="result")
        self.assertIsNone(serializer)

    def test_get_serializer_class_action_success(self):
        fields_config = {
            "name": fields.CharField(max_length=255),
            "age": fields.IntegerField(),
        }

        serializer_class = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )

        view = create_view_with_custom_action(
            action_name="custom_action",
            action_serializer_class=serializer_class,
            action_kwargs={"methods": ["GET"], "detail": False},
        )
        view.schema = AudomaAutoSchema()
        view.request = self.factory.get("/example/")
        view.action = "custom_action"
        serializer = view.schema._get_serializer(serializer_type="result")

        self.assertEqual(type(serializer), serializer_class)

    def test_get_serializer_class_audoma_action_success(self):
        fields_config = {
            "name": fields.CharField(max_length=255),
            "age": fields.IntegerField(),
        }

        serializer_class = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )

        view = create_view_with_custom_audoma_action(
            action_name="custom_action",
            action_serializer_class=serializer_class,
            action_kwargs={"methods": ["GET"], "detail": False},
        )
        view.schema = AudomaAutoSchema()
        view.request = self.factory.get("/example/")
        view.action = "custom_action"
        serializer = view.schema._get_serializer(serializer_type="result")

        self.assertEqual(type(serializer), serializer_class)

    def test_get_serializer_class_audoma_action_custom_responses_and_collectors(self):
        # response serializer
        fields_config = {
            "name": fields.CharField(max_length=255),
            "age": fields.IntegerField(),
            "is_admin": fields.BooleanField(),
        }

        result_serializer_class = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )
        # collect serializer

        fields_config = {
            "name": fields.CharField(max_length=255),
            "age": fields.IntegerField(),
        }

        collect_serializer_class = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )

        request = self.factory.post("/example/", data={})

        view = create_view_with_custom_audoma_action(
            action_name="custom_action",
            action_kwargs={
                "methods": ["POST"],
                "detail": False,
                "collectors": {"post": collect_serializer_class},
                "results": {"post": {"201": result_serializer_class}},
            },
        )
        # in our case we have to call action to set some attrs

        view.request = request
        view.action = "custom_action"
        view.schema = AudomaAutoSchema()
        serializer = view.schema._get_serializer(serializer_type="result")

        self.assertEqual(type(serializer), dict)
        self.assertEqual(type(serializer["201"]), result_serializer_class)

        serializer = view.schema._get_serializer(serializer_type="collect")
        self.assertEqual(serializer, collect_serializer_class)

    def test_get_serializer_class_audoma_action_string_response_success(self):
        # response serializer
        request = self.factory.post("/example/", data={})

        view = create_view_with_custom_audoma_action(
            action_name="custom_action",
            action_kwargs={
                "methods": ["POST"],
                "detail": False,
                "results": "Test message",
            },
        )
        # in our case we have to call action to set some attrs

        view.request = request
        view.action = "custom_action"
        view.schema = AudomaAutoSchema()
        serializer = view.schema._get_serializer(serializer_type="result")

        self.assertEqual(type(serializer), dict)
        self.assertEqual(serializer["default"].description, "Test message")

    def test_map_serializer_field_charfield_success(self):
        fields_config = {
            "name": fields.CharField(max_length=255),
            "age": fields.IntegerField(),
            "is_admin": fields.BooleanField(),
        }

        serializer = create_serializer(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )
        serializer_fields = serializer.fields
        request = self.factory.get("/example/")
        view = create_basic_view(view_properties={"serializer_class": type(serializer)})

        view.request = request
        view.action = "retrieve"
        view.schema = AudomaAutoSchema()
        mapped_field = view.schema._map_serializer_field(
            serializer_fields["name"], direction="response"
        )
        self.assertEqual(type(mapped_field), dict)
        self.assertEqual(mapped_field["type"], "string")

    def test_map_serializer_field_choicefield_xchoices_success(self):
        fields_config = {
            "company_name": fields.CharField(max_length=255),
            "company_size": fields.ChoiceField(
                choices=(("SMALL", "small"), ("MEDIUM", "medium"), ("LARGE", "large"))
            ),
        }
        serializer = create_serializer(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )
        serializer_fields = serializer.fields

        request = self.factory.get("/example/")
        view = create_basic_view(view_properties={"serializer_class": type(serializer)})
        view.request = request
        view.action = "retrieve"
        view.schema = AudomaAutoSchema()
        mapped_field = view.schema._map_serializer_field(
            serializer_fields["company_size"], direction="response"
        )
        self.assertEqual(type(mapped_field), dict)
        self.assertEqual(mapped_field["type"], "string")
        self.assertEqual(type(mapped_field["x-choices"]), dict)
        self.assertEqual(
            mapped_field["x-choices"],
            {"choices": {"SMALL": "small", "MEDIUM": "medium", "LARGE": "large"}},
        )

    def test_map_serializer_field_audoma_choicefield_xchoices_success(self):
        fields_config = {
            "company_name": audoma_fields.CharField(max_length=255),
            "company_size": audoma_fields.ChoiceField(
                choices=(("SMALL", "small"), ("MEDIUM", "medium"), ("LARGE", "large"))
            ),
        }
        serializer = create_serializer(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )
        serializer_fields = serializer.fields

        request = self.factory.get("/example/")
        view = create_basic_view(view_properties={"serializer_class": type(serializer)})
        view.request = request
        view.action = "retrieve"
        view.schema = AudomaAutoSchema()
        mapped_field = view.schema._map_serializer_field(
            serializer_fields["company_size"], direction="response"
        )
        self.assertEqual(type(mapped_field), dict)
        self.assertEqual(mapped_field["type"], "string")
        self.assertEqual(type(mapped_field["x-choices"]), dict)
        self.assertEqual(
            mapped_field["x-choices"],
            {"choices": {"SMALL": "small", "MEDIUM": "medium", "LARGE": "large"}},
        )

    def test_get_request_for_media_type_is_bulk_create(self):
        fields_config = {
            "company_name": audoma_fields.CharField(max_length=255),
            "company_size": audoma_fields.CharField(),
        }
        serializer_class = create_serializer_class(
            fields_config=fields_config,
            serializer_base_classes=[
                Serializer,
                audoma_serializers.BulkSerializerMixin,
            ],
        )
        serializer = serializer_class()
        request = self.factory.post("/example/")
        view = create_basic_view(view_properties={"serializer_class": serializer_class})
        view.request = request
        view.action = "create"
        view.schema = AudomaAutoSchema()
        view.schema.registry = ComponentRegistry()
        view.schema.method = "POST"
        view.schema.is_bulk = True
        schema, _ = view.schema._get_request_for_media_type(serializer)
        self.assertEqual(type(schema), dict)
        self.assertEqual(type(schema["oneOf"]), list)
        self.assertEqual(type(schema["oneOf"][0]), dict)
        self.assertEqual(schema["oneOf"][0]["type"], "array")

    def test_get_request_for_media_type_is_bulk_update(self):
        fields_config = {
            "company_name": audoma_fields.CharField(max_length=255),
            "company_size": audoma_fields.CharField(),
        }
        serializer_class = create_serializer_class(
            fields_config=fields_config,
            serializer_base_classes=[
                Serializer,
                audoma_serializers.BulkSerializerMixin,
            ],
        )
        serializer = serializer_class()
        request = self.factory.put("/example/")
        view = create_basic_view(view_properties={"serializer_class": serializer_class})
        view.request = request
        view.action = "update"
        view.schema = AudomaAutoSchema()
        view.schema.registry = ComponentRegistry()
        view.schema.method = "PUT"
        view.schema.is_bulk = True
        schema, _ = view.schema._get_request_for_media_type(serializer)
        self.assertEqual(type(schema), dict)
        self.assertEqual(schema["type"], "array")

    def test_get_request_for_media_type_is_not_bulk(self):
        fields_config = {
            "company_name": audoma_fields.CharField(max_length=255),
            "company_size": audoma_fields.CharField(),
        }
        serializer_class = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )
        serializer = serializer_class()
        request = self.factory.post("/example/")
        view = create_basic_view(view_properties={"serializer_class": serializer_class})
        view.request = request
        view.action = "create"
        view.schema = AudomaAutoSchema()
        view.schema.registry = ComponentRegistry()
        view.schema.method = "POST"
        view.schema.is_bulk = False
        schema, _ = view.schema._get_request_for_media_type(serializer)
        self.assertEqual(type(schema), dict)
        self.assertEqual(schema["$ref"], "#/components/schemas/ExampleRequest")

    def test_map_serializer_default_serializer(self):
        fields_config = {
            "company_name": audoma_fields.CharField(max_length=255),
            "company_size": audoma_fields.CharField(),
        }
        serializer_class = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )
        serializer = serializer_class()
        request = self.factory.post("/example/")
        view = create_basic_view(view_properties={"serializer_class": serializer_class})
        view.request = request
        view.action = "create"
        view.schema = AudomaAutoSchema()
        view.schema.registry = ComponentRegistry()
        view.schema.method = "POST"
        view.schema.is_bulk = False
        schema = view.schema._map_serializer(serializer, direction="request")
        self.assertEqual(type(schema), dict)
        self.assertIn("company_name", schema["properties"])
        self.assertIn("company_size", schema["properties"])

    def test_map_serializer_with_exclusive_fields(self):
        fields_config = {
            "company_name": audoma_fields.CharField(max_length=255),
            "customer_name": audoma_fields.CharField(max_length=255),
        }
        serializer_class = create_serializer_class(
            fields_config=fields_config,
            serializer_base_classes=[Serializer],
            validators=[
                ExclusiveFieldsValidator(fields=["company_name", "customer_name"])
            ],
        )
        serializer = serializer_class()
        request = self.factory.post("/example/")
        view = create_basic_view(view_properties={"serializer_class": serializer_class})
        view.request = request
        view.action = "create"
        view.schema = AudomaAutoSchema()
        view.schema.registry = ComponentRegistry()
        view.schema.method = "POST"
        view.schema.is_bulk = False
        schema = view.schema._map_serializer(serializer, direction="request")
        self.assertEqual(type(schema["oneOf"]), list)
        self.assertIn("customer_name", schema["oneOf"][0]["properties"])
        self.assertNotIn("company_name", schema["oneOf"][0]["properties"])
        self.assertNotIn("customer_name", schema["oneOf"][1]["properties"])
        self.assertIn("company_name", schema["oneOf"][1]["properties"])

    def test_get_operation_id_bulk_create(self):
        fields_config = {
            "company_name": audoma_fields.CharField(max_length=255),
            "customer_name": audoma_fields.CharField(max_length=255),
        }
        serializer_class = create_serializer_class(
            fields_config=fields_config,
            serializer_base_classes=[Serializer],
            validators=[
                ExclusiveFieldsValidator(fields=["company_name", "customer_name"])
            ],
        )
        request = self.factory.post("/example/")
        view = create_basic_view(view_properties={"serializer_class": serializer_class})
        view.request = request
        view.action = "create"
        view.schema = AudomaAutoSchema()
        view.schema.registry = ComponentRegistry()
        view.schema.method = "POST"
        view.schema.is_bulk = True
        view.schema.path = "/example/"
        view.schema.path_prefix = ""
        view.schema.path_regex = r"\/\w\/"
        operation_id = view.schema.get_operation_id()
        self.assertIn("bulk", operation_id)

    def test_get_operation_id_bulk_upadte(self):
        fields_config = {
            "company_name": audoma_fields.CharField(max_length=255),
            "customer_name": audoma_fields.CharField(max_length=255),
        }
        serializer_class = create_serializer_class(
            fields_config=fields_config,
            serializer_base_classes=[Serializer],
            validators=[
                ExclusiveFieldsValidator(fields=["company_name", "customer_name"])
            ],
        )
        request = self.factory.post("/example/")
        view = create_basic_view(view_properties={"serializer_class": serializer_class})
        view.request = request
        view.action = "create"
        view.schema = AudomaAutoSchema()
        view.schema.registry = ComponentRegistry()
        view.schema.method = "POST"
        view.schema.is_bulk = False
        view.schema.path = "/example/"
        view.schema.path_prefix = ""
        view.schema.path_regex = r"\/\w\/"
        operation_id = view.schema.get_operation_id()
        self.assertNotIn("bulk", operation_id)
