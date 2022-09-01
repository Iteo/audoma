from django_filters.filters import (
    ChoiceFilter,
    TypedChoiceFilter,
)
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.plumbing import ComponentRegistry
from rest_framework.filters import SearchFilter
from rest_framework.serializers import Serializer
from rest_framework.test import APIRequestFactory

from django.db import models
from django.test import TestCase

from audoma.choices import make_choices
from audoma.drf import fields as audoma_fields
from audoma.drf.filters import DocumentedTypedChoiceFilter
from audoma.openapi import AudomaAutoSchema
from audoma.schema import (
    AudomaDjangoFilterExtension,
    SearchFilterExtension,
)
from audoma.tests.testtools import (
    create_basic_view,
    create_model_class,
    create_serializer_class,
)


class AudomaDjangoFilterExtensionTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.choices = make_choices(
            "RATE", ((0, "LIKE", "Like"), (1, "DISLIKIE", "Dislike"))
        )
        self.fields_config = {
            "company_name": audoma_fields.CharField(max_length=255),
            "city": audoma_fields.CharField(),
            "company_rate": audoma_fields.ChoiceField(
                choices=self.choices.get_choices()
            ),
        }
        serializer_class = create_serializer_class(
            fields_config=self.fields_config,
            serializer_base_classes=[Serializer],
        )
        request = self.factory.post("/example/")
        self.model_fields_config = {
            "company_name": models.CharField(max_length=255),
            "city": models.CharField(max_length=255),
            "company_rate": models.CharField(choices=self.choices.get_choices()),
        }
        model = create_model_class(fields_config=self.model_fields_config)
        self.view = create_basic_view(
            view_properties={"serializer_class": serializer_class}
        )
        self.view.request = request
        self.view.action = "create"
        self.view.schema = AudomaAutoSchema()
        self.view.schema.registry = ComponentRegistry()
        self.view.schema.method = "POST"
        self.view.model = model
        self.extension = AudomaDjangoFilterExtension(target=DjangoFilterBackend())

    def test_get_audoma_documented_typed_choice_filter_x_choices(self):
        field = DocumentedTypedChoiceFilter(
            full_choices=self.choices, parameter_name="company_rate"
        )
        result = self.extension.resolve_filter_field(
            self.view.schema, self.view.model, None, "company_rate", field
        )
        self.assertIsInstance(result, list)
        self.assertEqual(
            result,
            [
                {
                    "in": "query",
                    "name": "company_rate",
                    "schema": {
                        "type": "string",
                        "enum": ["DISLIKIE", "LIKE"],
                        "x-choices": {
                            "choices": {"LIKE": "Like", "DISLIKIE": "Dislike"}
                        },
                    },
                    "description": "Filter by None \n * `LIKE` - Like\n * `DISLIKIE` - Dislike\n",
                }
            ],
        )

    def test_get_typed_choice_filter_x_choices(self):
        field = TypedChoiceFilter(
            choices=self.choices.get_api_choices(), parameter_name="company_rate"
        )
        result = self.extension.resolve_filter_field(
            self.view.schema, self.view.model, None, "company_rate", field
        )
        self.assertEqual(
            result[0]["schema"]["x-choices"],
            {"choices": {"LIKE": "Like", "DISLIKIE": "Dislike"}},
        )

    def test_get_choice_filter_x_choices(self):
        field = ChoiceFilter(
            choices=self.choices.get_api_choices(), parameter_name="company_rate"
        )
        result = self.extension.resolve_filter_field(
            self.view.schema, self.view.model, None, "company_rate", field
        )
        self.assertEqual(
            result[0]["schema"]["x-choices"],
            {"choices": {"LIKE": "Like", "DISLIKIE": "Dislike"}},
        )

    def test_get_x_choices_no_choices(self):
        field = ChoiceFilter()
        result = self.extension.resolve_filter_field(
            self.view.schema, self.view.model, None, "company_rate", field
        )
        self.assertEqual(result, [])


class SearchFilterExtensionTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.choices = make_choices(
            "RATE", ((0, "LIKE", "Like"), (1, "DISLIKIE", "Dislike"))
        )
        self.fields_config = {
            "company_name": audoma_fields.CharField(max_length=255),
            "city": audoma_fields.CharField(),
            "company_rate": audoma_fields.ChoiceField(
                choices=self.choices.get_choices()
            ),
        }
        serializer_class = create_serializer_class(
            fields_config=self.fields_config,
            serializer_base_classes=[Serializer],
        )
        request = self.factory.post("/example/")
        self.model_fields_config = {
            "company_name": models.CharField(max_length=255),
            "city": models.CharField(max_length=255),
            "company_rate": models.CharField(choices=self.choices.get_choices()),
        }
        model = create_model_class(fields_config=self.model_fields_config)
        self.view = create_basic_view(
            view_properties={"serializer_class": serializer_class}
        )
        self.view.request = request
        self.view.action = "create"
        self.view.schema = AudomaAutoSchema()
        self.view.schema.registry = ComponentRegistry()
        self.view.schema.method = "POST"
        self.view.model = model
        self.view.search_fields = ["company_name", "city"]
        self.extension = SearchFilterExtension(target=SearchFilter())

    def test_search_filter_generate_default_description(self):
        result = self.extension.get_schema_operation_parameters(self.view.schema)
        self.assertEqual(
            result[0]["description"], "Search by: \n* `company_name` \n* `city` \n"
        )

    def test_search_filter_generate_custom_simple_description(self):
        self.extension.target.search_description = (
            "Some Custom description.\n {search_fields}"
        )
        result = self.extension.get_schema_operation_parameters(self.view.schema)
        self.assertEqual(
            result[0]["description"],
            "Some Custom description.\n Search by: \n* `company_name` \n* `city` \n",
        )
