import json
from datetime import (
    date,
    timedelta,
)

from audoma_api.views import (
    ExampleModelPermissionLessViewSet,
    ExampleModelViewSet,
    ExampleViewSet,
)
from drf_example.urls import router
from drf_spectacular.generators import SchemaGenerator
from rest_framework.permissions import BasePermission
from rest_framework.test import (
    APIClient,
    APIRequestFactory,
)

from django.shortcuts import reverse
from django.test import (
    SimpleTestCase,
    override_settings,
)

from audoma.decorators import AudomaActionException
from audoma.drf.viewsets import AudomaPagination


class AudomaTests(SimpleTestCase):
    def setUp(self):
        patterns = router.urls
        generator = SchemaGenerator(patterns=patterns)
        self.schema = generator.get_schema(request=None, public=True)
        self.redoc_schemas = self.schema["components"]["schemas"]

    def test_extend_schema_fields_with_example(self):
        phone_number_field = self.redoc_schemas["Example"]["properties"]["phone_number"]
        mac_address_field = self.redoc_schemas["Example"]["properties"]["mac_address"]
        regex_field = self.redoc_schemas["Example"]["properties"]["regex_mac_address"]
        expected_phone_number_field = {
            "type": "string",
            "format": "tel",
            "example": "+1 8888888822",
        }
        self.assertTrue("example" in mac_address_field and "type" in mac_address_field)
        self.assertTrue("example" in regex_field and "type" in regex_field)
        self.assertEqual(expected_phone_number_field, phone_number_field)

    def test_extend_schema_field_with_example_as_init(self):
        date_field = self.redoc_schemas["Example"]["properties"]["date"]
        time_field = self.redoc_schemas["Example"]["properties"]["time"]
        expected_date_field = {
            "type": "string",
            "format": "date",
            "example": str(date.today()),
        }
        expected_time_field = {
            "type": "string",
            "format": "time",
            "example": "12:34:56.000000",
        }
        self.assertEqual(expected_date_field, date_field)
        self.assertEqual(expected_time_field, time_field)

    def test_extend_schema_field_with_openapitype(self):
        uuid_field = self.redoc_schemas["Example"]["properties"]["uuid"]
        expected_uuid_field = {"type": "string", "format": "uuid"}
        self.assertEqual(expected_uuid_field, uuid_field)

    def test_model_mapping_all_field_serializer(self):
        example_model_properties = self.redoc_schemas["ExampleModel"]["properties"]
        self.assertEqual(20, len(example_model_properties))

    def test_filter_params_description_model_viewset(self):
        choices_desc = "Filter by choice \n * `EX_1` - example 1\n * `EX_2` - example 2\n * `EX_3` - example 3\n"
        docs_description = self.schema["paths"]["/model_examples/"]["get"][
            "parameters"
        ][0]["description"]
        self.assertEqual(choices_desc, docs_description)

    def test_permission_description_extension_model_viewset(self):
        expected_permissions = ExampleModelViewSet.permission_classes
        description = self.schema["paths"]["/model_examples/"]["get"]["description"]
        for permission in expected_permissions:
            # skip operations
            if not isinstance(permission, BasePermission):
                continue
            self.assertIn(str(permission.__name__), description)

    def test_permission_description_extension_standard_viewset(self):
        expected_permissions = ExampleViewSet.permission_classes
        description = self.schema["paths"]["/examples/"]["get"]["description"]
        for permission in expected_permissions:
            # skip operations
            if not isinstance(permission, BasePermission):
                continue
            self.assertIn(str(permission.__name__), description)

    def test_document_and_format_example_model_phone_number(self):
        example_model_properties = self.redoc_schemas["ExampleModel"]["properties"]
        phone_number = example_model_properties["phone_number"]
        self.assertEqual("tel", phone_number["format"])
        self.assertEqual("+1 8888888822", phone_number["example"])

    def test_custom_paginated_response_schema(self):
        paginated_example = self.redoc_schemas["PaginatedExampleList"]
        paginator = AudomaPagination()
        expected_pagination = paginator.get_paginated_response_schema(paginated_example)
        self.assertEqual(
            paginated_example["properties"].keys(),
            expected_pagination["properties"].keys(),
        )

    def test_file_upload_view_parsers(self):
        example_schema = self.schema["paths"]["/file-upload-example/"]["post"][
            "requestBody"
        ]["content"]
        self.assertEqual(len(example_schema.keys()), 1)
        self.assertEqual(list(example_schema.keys())[0], "multipart/form-data")
        example_model_properties = self.redoc_schemas["ExampleModel"]["properties"]
        phone_number = example_model_properties["phone_number"]
        self.assertEqual("tel", phone_number["format"])
        self.assertEqual("+1 8888888822", phone_number["example"])

    def test_default_response_in_view_responses(self):
        docs = self.schema["paths"][
            "/permissionless_model_examples/properly_defined_exception_example/"
        ]
        responses_docs = docs["get"]["responses"]
        self.assertEqual(
            responses_docs["default"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/ExampleOneField",
        )

    def test_custom_responses_in_view_responses(self):
        docs = self.schema["paths"][
            "/permissionless_model_examples/{id}/detail_action/"
        ]
        responses_docs = docs["post"]["responses"]
        self.assertEqual(
            responses_docs["201"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/ExampleModel",
        )
        self.assertEqual(
            responses_docs["202"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/ExampleOneField",
        )

    def test_common_errors_in_description(self):
        expected_error_data = '\n {\n    "detail": "Not found."\n} \n'
        self.assertIn(expected_error_data, self.schema["info"]["description"])
        expected_error_data = ' \n {\n    "detail": "Authentication credentials were not provided."\n} \n '
        self.assertIn(expected_error_data, self.schema["info"]["description"])

    def test_viewset_errors_in_viewset_responses(self):
        docs = self.schema["paths"][
            "/permissionless_model_examples/properly_defined_exception_example/"
        ]
        responses_docs = docs["get"]["responses"]
        self.assertEqual(
            responses_docs["400"]["content"]["application/json"]["schema"]["example"][
                "detail"
            ],
            "Custom Bad Request Exception",
        )
        self.assertEqual(
            responses_docs["409"]["content"]["application/json"]["schema"]["example"][
                "detail"
            ],
            "Conflict has occured",
        )


class AudomaViewsTestCase(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.data = {
            "char_field": "TESTChar",
            "phone_number": "+18888888822",
            "email": "test@iteo.com",
            "url": "http://localhost:8000/redoc/",
            "boolean": False,
            "nullboolean": None,
            "mac_adress": "96:82:2E:6B:F5:49",
            "slug": "tst",
            "uuid": "14aefe15-7c96-49b6-9637-7019c58c25d2",
            "ip_address": "192.168.10.1",
            "integer": 16,
            "_float": 12.2,
            "decimal": "13.23",
            "datetime": "2009-11-13T10:39:35Z",
            "date": "2009-11-13",
            "time": "10:39:35",
            "duration": timedelta(days=1),
            "choices": 1,
            "json": "",
        }
        self.client = APIClient()

    def test_detail_action_get(self):
        response = self.client.get(
            reverse("permissionless-model-examples-detail-action", kwargs={"pk": 0})
        )
        self.assertEqual(response.status_code, 405)

    def test_detail_action_post_with_usertype(self):
        self.data["usertype"] = "admin"
        response = self.client.post(
            reverse("permissionless-model-examples-detail-action", kwargs={"pk": 0}),
            self.data,
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        response_content = json.loads(response.content)
        self.assertEqual(self.data["char_field"], response_content["char_field"])
        self.assertEqual(self.data["mac_adress"], response_content["mac_adress"])
        self.assertEqual(self.data["uuid"], response_content["uuid"])

    def test_detail_action_post_without_usertype(self):
        response = self.client.post(
            reverse("permissionless-model-examples-detail-action", kwargs={"pk": 0}),
            self.data,
            format="json",
        )
        self.assertEqual(response.status_code, 202)
        response_content = json.loads(response.content)
        self.assertEqual(response_content["rate"], 0)

    def test_non_detail_action_get(self):
        response = self.client.get(
            reverse("permissionless-model-examples-non-detail-action")
        )
        content = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["message"], "This is a test view")

    def test_rate_create_action_post_success(self):
        response = self.client.post(
            reverse("permissionless-model-examples-rate-create-action"),
            {"rate": 1},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content)["rate"], 1)

    def test_rate_create_action_post_failure(self):
        response = self.client.post(
            reverse("permissionless-model-examples-rate-create-action")
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content["errors"]["rate"], "This field is required.")

    def test_specific_rate_get_success(self):
        response = self.client.get(
            reverse("permissionless-model-examples-specific-rate", kwargs={"pk": 1})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["rate"], 1)

    @override_settings(DEBUG=True)
    def test_properly_defined_exception_example(self):
        response = self.client.get(
            reverse("permissionless-model-examples-properly-defined-exception-example")
        )
        self.assertEqual(response.status_code, 409)
        content = json.loads(response.content)
        self.assertEqual(
            content["errors"]["detail"], "Some custom message, that should be accepted"
        )

    def test_proper_usage_of_common_errors(self):
        response = self.client.get(
            reverse("permissionless-model-examples-proper-usage-of-common-errors")
        )
        self.assertEqual(response.status_code, 404)
        content = json.loads(response.content)
        self.assertEqual(content["errors"]["detail"], "Not found.")

    @override_settings(DEBUG=True)
    def test_improperly_defined_exception_example_debug_true(self):
        try:
            view = ExampleModelPermissionLessViewSet()
            url = reverse(
                "permissionless-model-examples-improperly-defined-exception-example"
            )
            factory = APIRequestFactory()
            request = factory.get(url)
            view.improperly_defined_exception_example(request)

        except Exception as e:
            self.assertEqual(type(e), AudomaActionException)
            self.assertIn(
                "<class 'audoma_api.exceptions.CustomBadRequestException'>", str(e)
            )

    def test_improperly_defined_exception_example_debug_false(self):
        response = self.client.get(
            reverse(
                "permissionless-model-examples-improperly-defined-exception-example"
            )
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["errors"]["detail"], "Custom Bad Request Exception")

    def test_example_update_action_patch(self):
        response = self.client.patch(
            reverse(
                "permissionless-model-examples-example-update-action", kwargs={"pk": 0}
            ),
            {"char_field": "TESTChar2", "email": "changetest@iteo.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content)["char_field"], "TESTChar2")
        self.assertEqual(json.loads(response.content)["email"], "changetest@iteo.com")

    def test_example_update_action_put(self):
        data = self.data
        data["char_field"] = "TESTChar2"
        response = self.client.put(
            reverse(
                "permissionless-model-examples-example-update-action", kwargs={"pk": 0}
            ),
            data,
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content)["char_field"], "TESTChar2")
