import json
import re
from datetime import (
    date,
    timedelta,
)

import phonenumbers
from audoma_api.models import (
    ExampleModel,
    Manufacturer,
)
from audoma_api.serializers import (
    ExampleModelSerializer,
    ExampleSerializer,
)
from audoma_api.views import (
    ExampleModelPermissionLessViewSet,
    ExampleModelViewSet,
    ExampleViewSet,
)
from drf_example.urls import router
from drf_spectacular.generators import SchemaGenerator
from phonenumber_field.phonenumber import to_python
from rest_framework.permissions import BasePermission
from rest_framework.test import (
    APIClient,
    APIRequestFactory,
    APITestCase,
)

from django.conf import settings
from django.shortcuts import reverse
from django.test import (
    SimpleTestCase,
    override_settings,
)

from audoma.decorators import AudomaActionException
from audoma.django.db import models
from audoma.drf import serializers
from audoma.drf.viewsets import AudomaPagination
from audoma.example_generators import generate_lorem_ipsum


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

    def test_filterset_class_description_in_query_params_schema(self):
        choices_desc = "Filter by choices \n * `EX_1` - example 1\n * `EX_2` - example 2\n * `EX_3` - example 3\n"
        docs_description = self.schema["paths"]["/model_examples/"]["get"][
            "parameters"
        ][0]["description"]
        self.assertEqual(choices_desc, docs_description)

    def test_filterset_fields_description_in_query_paramas_schema(self):
        choices_desc = "Filter by engine_type \n * `1` - Petrol\n * `2` - Diesel\n * `3` - Electric\n * `4` - Hybrid\n"
        docs_description = self.schema["paths"]["/car_viewset/"]["get"]["parameters"][
            0
        ]["description"]
        self.assertEqual(choices_desc, docs_description)

    def test_search_fields_description(self):
        expected_search_description = (
            "Search by: \n* `manufacturer(Exact matches.)` \n* `name` \n"
        )

        docs_description = self.schema["paths"]["/car_viewset/"]["get"]["parameters"]
        search_docs_data = docs_description[-1]
        self.assertEqual(search_docs_data["name"], "search")
        self.assertEqual(search_docs_data["description"], expected_search_description)

    def test_x_choices_enum_serializer(self):
        expected_choices = {
            1: "Sedan",
            2: "Coupe",
            3: "Hatchback",
            4: "Pickup Truck",
        }
        choices_schema = self.schema["components"]["schemas"]["CarModel"]["properties"][
            "body_type"
        ]["x-choices"]["choices"]
        for key, item in choices_schema.items():
            self.assertEqual(item, expected_choices[key])

    def test_x_choices_enum_paramteres(self):
        expected_choices = {
            1: "Petrol",
            2: "Diesel",
            3: "Electric",
            4: "Hybrid",
        }
        choices_schema = self.schema["paths"]["/car_viewset/"]["get"]["parameters"][0][
            "schema"
        ]["x-choices"]["choices"]

        for key, item in choices_schema.items():
            self.assertEqual(item, expected_choices[key])

    def test_x_choices_link_serializer(self):
        expected_link = {
            "operationRef": "#/paths/~1manufacturer_viewset~1",
            "value": "$response.body#results/*/id",
            "display": "$response.body#results/*/name",
        }
        link_schema = self.schema["components"]["schemas"]["CarModel"]["properties"][
            "manufacturer"
        ]["x-choices"]
        for key, item in link_schema.items():
            self.assertEqual(item, expected_link[key])

    def test_charfield_example_limits(self):
        charfield_redoc = self.redoc_schemas["Example"]["properties"][
            "charfield_min_max"
        ]
        charfield_example = charfield_redoc["example"]
        charfield = ExampleSerializer.__dict__["_declared_fields"]["charfield_min_max"]
        min_length = charfield.min_length
        max_length = charfield.max_length
        self.assertLessEqual(min_length, len(charfield_example))
        self.assertGreaterEqual(max_length, len(charfield_example))

    def test_generate_lorem_ipsum_only_min_length(self):
        short_lorem_example = generate_lorem_ipsum(min_length=60)
        long_lorem_example = generate_lorem_ipsum(min_length=1024)
        self.assertGreaterEqual(len(short_lorem_example), 60)
        self.assertLessEqual(len(short_lorem_example), 80)
        self.assertGreaterEqual(len(long_lorem_example), 1024)

    def test_generate_lorem_ipsum_only_max_length(self):
        short_lorem_example = generate_lorem_ipsum(max_length=10)
        long_lorem_example = generate_lorem_ipsum(max_length=1024)
        self.assertLessEqual(len(short_lorem_example), 10)
        self.assertGreaterEqual(len(long_lorem_example), 20)
        self.assertLessEqual(len(long_lorem_example), 1024)

    def test_generate_lorem_ipsum_max_min(self):
        short_lorem_example = generate_lorem_ipsum(min_length=1, max_length=5)
        long_lorem_example = generate_lorem_ipsum(min_length=100, max_length=200)
        self.assertGreaterEqual(len(short_lorem_example), 1)
        self.assertLessEqual(len(short_lorem_example), 5)
        self.assertGreaterEqual(len(long_lorem_example), 100)
        self.assertLessEqual(len(long_lorem_example), 200)

    def test_example_money_currency_with_currency_from_settings(self):
        currency = self.redoc_schemas["ExampleModel"]["properties"]["money_currency"]
        self.assertIn(currency["example"], settings.CURRENCIES)

    def test_example_money_currency_with_default_currency(self):
        currency = self.redoc_schemas["ExamplePersonModel"]["properties"][
            "savings_currency"
        ]
        self.assertEqual("PLN", currency["example"])

    def test_mutually_exclusive_fields_schemas(self):
        schema = self.redoc_schemas["MutuallyExclusiveExampleRequest"]
        default_keys = ["not_exclusive_field", "second_not_exclusive_field"]
        self.assertEqual(len(schema["oneOf"]), 4)
        self.assertEqual(
            list(schema["oneOf"][0]["properties"].keys()),
            ["second_example_field", "third_example_field", "fourth_example_field"]
            + default_keys,
        )
        self.assertEqual(
            list(schema["oneOf"][1]["properties"].keys()),
            ["example_field", "third_example_field", "fourth_example_field"]
            + default_keys,
        )
        self.assertEqual(
            list(schema["oneOf"][2]["properties"].keys()),
            ["example_field", "second_example_field", "fourth_example_field"]
            + default_keys,
        )
        self.assertEqual(
            list(schema["oneOf"][3]["properties"].keys()),
            ["example_field", "second_example_field", "third_example_field"]
            + default_keys,
        )

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


class AudomaBulkOperationsTest(APITestCase):
    def setUp(self):
        self.list_url = reverse("bulk-example-list")
        Manufacturer.objects.bulk_create(
            [
                Manufacturer(name="Example 1", slug_name="ex_1"),
                Manufacturer(name="Example 2", slug_name="ex_2"),
            ]
        )
        return super().setUp()

    def test_bulk_create_records(self):
        data = [
            {
                "name": "test 1",
                "slug_name": "2138",
            },
            {
                "name": "test 2",
                "slug_name": "2137",
            },
        ]

        resp = self.client.post(self.list_url, data, format="json")
        self.assertEqual(201, resp.status_code, resp.json())

        qs = Manufacturer.objects.all()
        self.assertEqual(qs.count(), 4)

    def test_bulk_create_single_record(self):
        data = (
            {
                "name": "test 2",
                "slug_name": "2137",
            },
        )

        resp = self.client.post(self.list_url, data, format="json")
        self.assertEqual(201, resp.status_code, resp.json())

        qs = Manufacturer.objects.all()
        self.assertEqual(qs.count(), 3)

    def test_bulk_update_records(self):
        updated_data = [
            {
                "id": 1,
                "name": "test 1 updated",
                "slug_name": "11",
            },
            {
                "id": 2,
                "name": "test 2 updated",
                "slug_name": "22",
            },
        ]

        resp = self.client.put(self.list_url, updated_data, format="json")
        qs = Manufacturer.objects.all()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(qs.first().name, "test 1 updated")
        self.assertEqual(qs.last().name, "test 2 updated")
        self.assertEqual(qs.first().slug_name, "11")
        self.assertEqual(qs.last().slug_name, "22")

    def test_bulk_partial_update_records(self):

        updated_data = [
            {
                "id": 1,
                "name": "test 1 updated",
            },
            {
                "id": 2,
                "name": "test 2 updated",
            },
        ]

        resp = self.client.patch(self.list_url, updated_data, format="json")
        qs = Manufacturer.objects.all()
        self.assertEqual(resp.status_code, 200, resp.json())
        self.assertEqual(qs.first().name, "test 1 updated")
        self.assertEqual(qs.last().name, "test 2 updated")
        self.assertEqual(qs.first().slug_name, "ex_1")
        self.assertEqual(qs.last().slug_name, "ex_2")

    # def test_bulk_delete_records(self):
    #     ExampleSimpleModel.objects.bulk_create(
    #         [
    #             ExampleSimpleModel(name="EX1", value=1),
    #             ExampleSimpleModel(name="EX2", value=2),
    #         ]
    #     )
    #     resp = self.client.delete(
    #         self.list_url, data=[{"name": "EX1"}, {"name": "EX2"}], format="json"
    #     )
    #     self.assertEqual(resp.status_code, 204)
    #     self.assertEqual(
    #         ExampleSimpleModel.objects.filter(name__in=["EX1", "EX2"]).count(), 0
    #     )

    def test_bulk_partial_update_records_invalid_pk(self):

        updated_data = [
            {
                "id": 4,
                "name": "test 1 updated",
            },
            {
                "id": 5,
                "name": "test 2 updated",
            },
        ]

        resp = self.client.patch(self.list_url, updated_data, format="json")
        self.assertEqual(resp.status_code, 400)

    # def test_bulk_delete_validation(self):
    #     ExampleSimpleModel.objects.bulk_create(
    #         [
    #             ExampleSimpleModel(name="EX1", value=1),
    #             ExampleSimpleModel(name="EX2", value=2),
    #         ]
    #     )
    #     resp = self.client.delete(
    #         self.list_url, data=[{"name": "EX2"}, {"name": "EX3"}], format="json"
    #     )
    #     self.assertEqual(resp.status_code, 400)
    #     self.assertEqual(
    #         ExampleSimpleModel.objects.filter(name__in=["EX1", "EX2"]).count(), 0
    #     )


class AudomaViewsTestCase(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.data = {
            "char_field": "TESTChar",
            "phone_number": "+18888888822",
            "phone_number_example": "+18888888822",
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
            "money": "12.23",
            "text_field": "TESTText",
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
        self.assertEqual(response.data["char_field"], "TESTChar2")
        self.assertEqual(response.data["email"], "changetest@iteo.com")

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
        self.assertEqual(response.data["char_field"], "TESTChar2")

    def test_example_non_detail_many_action(self):
        response = self.client.get(
            reverse("permissionless-model-examples-example-many-test-action"),
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
