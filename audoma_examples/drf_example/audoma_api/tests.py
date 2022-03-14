import json
from datetime import date

from django.shortcuts import reverse
from django.test import SimpleTestCase
from drf_example.urls import router
from drf_spectacular.generators import SchemaGenerator
from rest_framework.permissions import BasePermission
from rest_framework.test import APIClient

from audoma_api.views import ExampleModelViewSet
from audoma_api.views import ExampleViewSet

from django.shortcuts import reverse
from django.test import SimpleTestCase

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


class AudomaViewsTestCase(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.data = {
            'char_field': "TESTChar",
            'phone_number': "(213) 444-1212",
            'email': "test@iteo.com",
            'url': "http://localhost:8000/redoc/",
            'char_field': 'TESTChar',
            'phone_number': '+18888888822',
            'email': 'test@iteo.com',
            'url': 'http://localhost:8000/redoc/',
            'boolean': False,
            'nullboolean': None,
            'mac_adress': '96:82:2E:6B:F5:49',
            'slug': 'tst',
            'uuid': '14aefe15-7c96-49b6-9637-7019c58c25d2',
            'ip_address': '192.168.10.1',
            'integer': 16,
            '_float': 12.2,
            'decimal': '13.23',
            'datetime': datetime.now(),# '2009-11-13T10:39:35Z',
            'date': date.today(), #'2009-11-13',
            'time': datetime.now().time(),#'10:39:35Z',
            'duration': timedelta(days=1),
            'choices': 1,
            'json': ''
        }
        self.client = APIClient()

    def test_detail_action_get(self):
        response = self.client.get(reverse('permissionless-model-examples-detail-action', kwargs={'pk': 0}))
        self.assertEqual(response.status_code, 405)
    
    def test_detail_action_post(self):
        response = self.client.post(
            reverse('permissionless-model-examples-detail-action', kwargs={'pk': 0}), self.data,
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        response_content = json.loads(response.content)
        self.assertEqual(self.data["char_field"], response_content["char_field"])
        self.assertEqual(self.data["mac_adress"], response_content["mac_adress"])
        self.assertEqual(self.data["uuid"], response_content["uuid"])

    def test_non_detail_action_get(self):
        response = self.client.get(reverse('permissionless-model-examples-non-detail-action'))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['message'], "This is a test view")

    def test_rate_create_action_post_success(self):
        response = self.client.post(
            reverse('permissionless-model-examples-rate-create-action'), {'rate': 1},
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content)['rate'], 1)

    def test_rate_create_action_post_failure(self):
        response = self.client.post(reverse('permissionless-model-examples-rate-create-action'))
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['errors']['rate'], "This field is required.")