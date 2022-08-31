from rest_framework import serializers
from rest_framework.test import APIRequestFactory

from django.test import TestCase

from audoma.tests import testtools


class GenericAPIViewTestCase(TestCase):
    def setUp(self):
        serializer_base_classes = (serializers.Serializer,)
        self.result_serializer_class = testtools.create_serializer_class(
            fields_config={"name": serializers.CharField(max_length=255)},
            serializer_base_classes=serializer_base_classes,
        )
        self.collect_serializer_class = testtools.create_serializer_class(
            fields_config={
                "name": serializers.CharField(max_length=255),
                "created_by": serializers.CharField(max_length=255),
            },
            serializer_base_classes=serializer_base_classes,
        )
        self.factory = APIRequestFactory()

    def test_get_serializer_result_success(self):
        viewset = testtools.create_basic_view(
            view_properties={
                "common_result_serializer_class": self.result_serializer_class
            },
        )
        viewset.action = "create"
        viewset.format_kwarg = "json"
        viewset.request = self.factory.post("/example/")
        serializer = viewset.get_result_serializer()
        self.assertEqual(type(serializer), self.result_serializer_class)

    def test_get_serializer_collect_success(self):
        viewset = testtools.create_basic_view(
            view_properties={
                "common_collect_serializer_class": self.collect_serializer_class
            },
        )
        viewset.action = "create"
        viewset.format_kwarg = "json"
        viewset.request = self.factory.post("/example/")
        serializer = viewset.get_serializer(serializer_type="collect")
        self.assertEqual(type(serializer), self.collect_serializer_class)

    def test_get_serializer_default_success(self):
        viewset = testtools.create_basic_view(
            view_properties={"serializer_class": self.result_serializer_class},
        )
        viewset.action = "create"
        viewset.format_kwarg = "json"
        viewset.request = self.factory.post("/example/")
        serializer = viewset.get_serializer(serializer_type="result")
        self.assertEqual(type(serializer), self.result_serializer_class)

    def test_get_serializer_result_many_success(self):
        viewset = testtools.create_basic_view(
            view_properties={
                "common_result_serializer_class": self.result_serializer_class
            },
        )
        viewset.action = "create"
        viewset.format_kwarg = "json"
        viewset.request = self.factory.post("/example/")
        serializer = viewset.get_result_serializer(many=True)
        self.assertEqual(type(serializer), serializers.ListSerializer)

    def test_get_serializer_collect_many_success(self):
        viewset = testtools.create_basic_view(
            view_properties={
                "common_collect_serializer_class": self.result_serializer_class
            },
        )
        viewset.action = "create"
        viewset.format_kwarg = "json"
        viewset.request = self.factory.post("/example/")
        serializer = viewset.get_serializer(many=True)
        self.assertEqual(type(serializer), serializers.ListSerializer)

    def test_get_serializer_class_audoma_action_result_success(self):
        viewset = testtools.create_view_with_custom_audoma_action(
            view_properties={"serializer_class": self.result_serializer_class},
            action_kwargs={
                "collectors": self.collect_serializer_class,
                "results": self.result_serializer_class,
                "detail": False,
                "methods": ["post"],
                "returnables": ({}, 201),
            },
        )
        viewset.action = "custom_action"
        viewset.format_kwarg = "json"
        viewset.request = self.factory.post("/example/")
        serializer = viewset.get_result_serializer()
        self.assertEqual(type(serializer), self.result_serializer_class)

    def test_get_serializer_class_audoma_action_collect_success(self):
        viewset = testtools.create_view_with_custom_audoma_action(
            view_properties={"serializer_class": self.result_serializer_class},
            action_kwargs={
                "collectors": self.collect_serializer_class,
                "results": self.result_serializer_class,
                "detail": False,
                "methods": ["post"],
                "returnables": ({}, 201),
            },
        )
        viewset.action = "custom_action"
        viewset.format_kwarg = "json"
        viewset.request = self.factory.post("/example/")
        serializer = viewset.get_serializer()
        self.assertEqual(type(serializer), self.collect_serializer_class)

    def test_get_serializer_class_audoma_action_result_method_nested_success(self):
        viewset = testtools.create_view_with_custom_audoma_action(
            view_properties={"serializer_class": self.result_serializer_class},
            action_kwargs={
                "collectors": self.collect_serializer_class,
                "results": {"post": self.result_serializer_class},
                "detail": False,
                "methods": ["post"],
                "returnables": ({}, 201),
            },
        )
        viewset.action = "custom_action"
        viewset.format_kwarg = "json"
        viewset.request = self.factory.post("/example/")
        serializer = viewset.get_result_serializer()
        self.assertEqual(type(serializer), self.result_serializer_class)

    def test_get_serializer_class_audoma_action_collect_method_nested_success(self):
        viewset = testtools.create_view_with_custom_audoma_action(
            view_properties={"serializer_class": self.result_serializer_class},
            action_kwargs={
                "collectors": {"post": self.collect_serializer_class},
                "results": self.result_serializer_class,
                "detail": False,
                "methods": ["post"],
                "returnables": ({}, 201),
            },
        )
        viewset.action = "custom_action"
        viewset.format_kwarg = "json"
        viewset.request = self.factory.post("/example/")
        serializer = viewset.get_serializer()
        self.assertEqual(type(serializer), self.collect_serializer_class)

    def test_get_serializer_class_audoma_action_result_method_code_nested_success(self):
        viewset = testtools.create_view_with_custom_audoma_action(
            view_properties={"serializer_class": self.result_serializer_class},
            action_kwargs={
                "collectors": self.collect_serializer_class,
                "results": {"post": {201: self.result_serializer_class}},
                "detail": False,
                "methods": ["post"],
                "returnables": ({}, 201),
            },
        )
        viewset.action = "custom_action"
        viewset.format_kwarg = "json"
        viewset.request = self.factory.post("/example/")
        serializer = viewset.get_result_serializer()
        self.assertEqual(type(serializer), self.result_serializer_class)

    def test_get_serializer_class_audoma_action_result_method_code_nested_failure(self):
        viewset = testtools.create_view_with_custom_audoma_action(
            action_kwargs={
                "collectors": self.collect_serializer_class,
                "results": {"post": {201: self.result_serializer_class}},
                "detail": False,
                "methods": ["post"],
                "returnables": ({}, 200),
            }
        )
        viewset.action = "custom_action"
        viewset.format_kwarg = "json"
        viewset.request = self.factory.post("/example/")
        try:
            viewset.get_result_serializer()
        except Exception as e:
            self.assertEquals(type(e), AssertionError)
            self.assertEquals(
                str(e),
                "'ExampleView' should either include a `serializer_class` "
                + " attribute, or override the `get_serializer_class()` method.",
            )
