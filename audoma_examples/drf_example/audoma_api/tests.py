from datetime import date

from audoma_api.views import (
    ExampleModelViewSet,
    ExampleViewSet,
)
from drf_example.urls import router
from drf_spectacular.generators import SchemaGenerator
from rest_framework.permissions import BasePermission

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

    def test_filter_params_description_model_viewset_documented_typed(self):
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
        
    def test_filterset_class_description_in_query_params_schema(self):
        choices_desc = "Filter by choices \n * `1` - example 1\n * `2` - example 2\n * `3` - example 3\n"
        docs_description = self.schema["paths"]["/example_filterset_class_viewset/"][
            "get"
        ]["parameters"][0]["description"]
        self.assertEqual(choices_desc, docs_description)

    def test_filterset_fields_description_in_query_paramas_schema(self):
        choices_desc = "Filter by choices \n * `1` - example 1\n * `2` - example 2\n * `3` - example 3\n"
        docs_description = self.schema["paths"]["/example_filterset_fields_viewset/"][
            "get"
        ]["parameters"][0]["description"]
        self.assertEqual(choices_desc, docs_description)

    def test_serach_fields_description(self):
        expected_search_description = (
            "Search by: \n* `foreign_key` \n\t * `name(Exact matches.)` \n* `name` \n"
        )

        docs_description = self.schema["paths"]["/example_related_model_viewset/"][
            "get"
        ]["parameters"]
        search_docs_data = docs_description[-1]
        self.assertEqual(search_docs_data["name"], "search")
        self.assertEqual(search_docs_data["description"], expected_search_description)

    def test_links_in_schema_list(self):
        schema_part = self.schema["paths"]["/example_related_model_viewset/"]["get"][
            "responses"
        ]["200"]["links"]
        self.assertEqual(type(schema_part["Example Foreign Key Viewset List"]), dict)

        details = schema_part["Example Foreign Key Viewset List"]
        self.assertEqual(details["description"], "")
        self.assertEqual(details["operationRef"], "/example_foreign_key_viewset/")
        self.assertEqual(details["parameters"], {"foreign_key": "$response.body#/id"})

    def test_links_in_schema_detail(self):
        schema_part = self.schema["paths"]["/example_related_model_viewset/{id}/"][
            "get"
        ]["responses"]["200"]["links"]
        self.assertEqual(type(schema_part["Example Foreign Key Viewset List"]), dict)

        details = schema_part["Example Foreign Key Viewset List"]
        self.assertEqual(details["description"], "")
        self.assertEqual(details["operationRef"], "/example_foreign_key_viewset/")
        self.assertEqual(details["parameters"], {"foreign_key": "$response.body#/id"})
