from datetime import date

from django.test import SimpleTestCase
from drf_example.urls import router
from drf_spectacular.generators import SchemaGenerator
from .views import example_choice


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
        expected_phone_number_field = {'type': 'string', 'format': 'tel', 'example': '+1 8888888822'}
        self.assertTrue('example' in mac_address_field and 'type' in mac_address_field)
        self.assertTrue('example' in regex_field and 'type' in regex_field)
        self.assertEqual(expected_phone_number_field, phone_number_field)

    def test_extend_schema_field_with_example_as_init(self):
        date_field = self.redoc_schemas["Example"]["properties"]["date"]
        time_field = self.redoc_schemas["Example"]["properties"]["time"]
        expected_date_field = {'type': 'string', 'format': 'date', 'example': str(date.today())}
        expected_time_field = {'type': 'string', 'format': 'time', 'example': '12:34:56.000000'}
        self.assertEqual(expected_date_field, date_field)
        self.assertEqual(expected_time_field, time_field)

    def test_extend_schema_field_with_openapitype(self):
        float_field = self.redoc_schemas["Example"]["properties"]["float"]
        uuid_field = self.redoc_schemas["Example"]["properties"]["uuid"]
        expected_float_field = {'type': 'number', 'format': 'float'}
        expected_uuid_field = {'type': 'string', 'format': 'uuid'}
        self.assertEqual(expected_float_field, float_field)
        self.assertEqual(expected_uuid_field, uuid_field)

    def test_model_mapping_all_field_serializer(self):
        example_model_properties = self.redoc_schemas["ExampleModel"]["properties"]
        self.assertEqual(20, len(example_model_properties))

    def test_create_openapi_description(self):
        example_model_params = self.schema["paths"]["/model_examples/"]["get"]["parameters"][0]
        schema = example_model_params["schema"]
        description = example_model_params["description"]
        self.assertEqual(example_choice.create_openapi_description().name, example_model_params['name'])
        self.assertEqual(example_choice.create_openapi_description().enum, tuple(schema['enum']))
        self.assertEqual(example_choice.create_openapi_description().description, description)

    def test_document_and_format_example_model_phone_number(self):
        example_model_properties = self.redoc_schemas['ExampleModel']['properties']
        phone_number = example_model_properties['phone_number']
        self.assertEqual('tel', phone_number['format'])
        self.assertEqual('+1 8888888822', phone_number['example'])
