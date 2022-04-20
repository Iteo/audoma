import re
from datetime import date

import phonenumbers
from audoma_api.models import ExampleModel
from audoma_api.serializers import ExampleModelSerializer
from audoma_api.views import (
    ExampleModelViewSet,
    ExampleViewSet,
)
from drf_example.urls import router
from drf_spectacular.generators import SchemaGenerator
from phonenumber_field.phonenumber import to_python
from rest_framework.permissions import BasePermission

from django.test import (
    SimpleTestCase,
    override_settings,
)

from audoma.django.db import models
from audoma.drf import serializers
from audoma.drf.viewsets import AudomaPagination


class AudomaTests(SimpleTestCase):
    def setUp(self):
        patterns = router.urls
        generator = SchemaGenerator(patterns=patterns)
        self.schema = generator.get_schema(request=None, public=True)
        self.redoc_schemas = self.schema["components"]["schemas"]

    def test_extend_schema_field_with_example_not_override_format(self):
        phone_number_field = self.redoc_schemas["Example"]["properties"][
            "phone_number_example"
        ]
        expected_phone_number_field = {
            "type": "string",
            "format": "tel",
            "example": "+48 123 456 789",
        }
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
        self.assertEqual(len(ExampleModel._meta.fields), len(example_model_properties))

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

    def test_custom_paginated_response_schema(self):
        paginated_example = self.redoc_schemas["PaginatedExampleList"]
        paginator = AudomaPagination()
        expected_pagination = paginator.get_paginated_response_schema(paginated_example)
        self.assertEqual(
            paginated_example["properties"].keys(),
            expected_pagination["properties"].keys(),
        )

    def test_example_float_field_with_range(self):
        float_field = self.redoc_schemas["Example"]["properties"]["float"]
        self.assertLessEqual(float_field["minimum"], float_field["example"])
        self.assertGreaterEqual(float_field["maximum"], float_field["example"])

    def test_example_mac_address_field_with_regex_mixin(self):
        example_mac_address = self.redoc_schemas["Example"]["properties"]["mac_address"]
        mac_address = serializers.MACAddressField()
        regex_pattern = re.compile(mac_address.regex)
        self.assertEqual(mac_address.regex, example_mac_address["pattern"])
        self.assertTrue(bool(regex_pattern.match(example_mac_address["example"])))

    def test_override_model_example_in_extra_kwargs(self):
        example_model_properties = self.redoc_schemas["ExampleModel"]["properties"]
        char_field = example_model_properties["char_field"]
        expected_result = ExampleModelSerializer.Meta.extra_kwargs["char_field"][
            "example"
        ]
        self.assertEqual(expected_result, char_field["example"])

    def test_example_models_custom_examples(self):
        example_person_properties = self.redoc_schemas["ExamplePersonModel"][
            "properties"
        ]
        first_name = example_person_properties["first_name"]
        last_name = example_person_properties["last_name"]
        self.assertEqual("Adam", first_name["example"])
        self.assertEqual("Smith", last_name["example"])

    def test_example_with_callable_as_argument(self):
        example_person_properties = self.redoc_schemas["ExamplePersonModel"][
            "properties"
        ]
        age = example_person_properties["age"]
        self.assertLessEqual(18, age["example"])
        self.assertGreaterEqual(80, age["example"])

    def test_model_phonenumber_with_region(self):
        example_person_properties = self.redoc_schemas["ExamplePersonModel"][
            "properties"
        ]
        phone_number_field = example_person_properties["phone_number"]
        phone_number_example = phone_number_field["example"]
        generated_france_number = to_python(
            phonenumbers.example_number("IT")
        ).as_international
        self.assertEqual(generated_france_number, phone_number_example)

    def test_phonenubber_example_region_international_format(self):

        pn = models.PhoneNumberField(region="PL")

        expected_example = to_python(phonenumbers.example_number("PL")).as_international
        self.assertEqual(expected_example, pn.example)

    @override_settings(PHONENUMBER_DEFAULT_FORMAT="NATIONAL")
    def test_phonenumber_example_region_national_format(self):
        pn = models.PhoneNumberField(region="PL")

        expected_example = to_python(phonenumbers.example_number("PL")).as_national
        self.assertEqual(expected_example, pn.example)

    @override_settings(PHONENUMBER_DEFAULT_FORMAT="E164")
    def test_phonenumber_example_region_e164_format(self):

        pn = models.PhoneNumberField(region="PL")

        expected_example = to_python(phonenumbers.example_number("PL")).as_e164
        self.assertEqual(expected_example, pn.example)

    def test_file_upload_view_parsers(self):
        example_schema = self.schema["paths"]["/file-upload-example/"]["post"][
            "requestBody"
        ]["content"]
        self.assertEqual(len(example_schema.keys()), 1)
        self.assertEqual(list(example_schema.keys())[0], "multipart/form-data")
