from django.test import TestCase

from audoma.choices import make_choices
from audoma.django.db import fields as db_fields
from audoma.drf import (
    fields,
    serializers,
)
from audoma.tests import testtools


class ResultTestCase(TestCase):
    def setUp(self):
        fields_config = {
            "name": fields.CharField(max_length=255),
            "age": fields.IntegerField(),
        }
        self.serializer_class = testtools.create_serializer_class(
            fields_config=fields_config,
            serializer_base_classes=(serializers.Serializer,),
        )

    def test_result_serializer_class_class_name_endswith_serializer(self):
        self.serializer_class.__name__ = "ExampleDetailSerializer"
        wrapped_serializer = serializers.result_serializer_class(self.serializer_class)
        self.assertEqual(wrapped_serializer.__name__, "ExampleDetailResultSerializer")

    def test_result_serializer_class_different_class_name(self):
        self.serializer_class.__name__ = "Example"
        wrapped_serializer = serializers.result_serializer_class(self.serializer_class)
        self.assertEqual(wrapped_serializer.__name__, "ExampleResult")

    def test_result_serializer_class_many(self):
        self.serializer_class.__name__ = "ExampleDetailSerializer"
        wrapped_serializer = serializers.result_serializer_class(self.serializer_class)
        self.assertTrue(hasattr(wrapped_serializer(many=True).instance, "results"))

    def test_result_serializer_class_not_many(self):
        self.serializer_class.__name__ = "ExampleDetailSerializer"
        wrapped_serializer = serializers.result_serializer_class(self.serializer_class)
        self.assertTrue(hasattr(wrapped_serializer().instance, "result"))


class ResultSerializerClassMixinTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.fields_config = {
            "name": serializers.CharField(max_length=255),
            "age": serializers.IntegerField(),
        }
        self.base_classes = (serializers.Serializer,)

    def test_wrap_serializer_class_many(self):
        serializer_class = testtools.create_serializer_class(
            fields_config=self.fields_config, serializer_base_classes=self.base_classes
        )
        serializer_class._wrap_result_serializer = True
        new_serializer_class = serializer_class.get_result_serializer_class()
        self.assertNotEqual(serializer_class, new_serializer_class)
        serializer = new_serializer_class(many=True)
        self.assertTrue(hasattr(serializer.instance, "results"))
        self.assertFalse(hasattr(serializer.instance, "result"))

    def test_wrap_serializer_class_not_many(self):

        serializer_class = testtools.create_serializer_class(
            fields_config=self.fields_config, serializer_base_classes=self.base_classes
        )
        serializer_class._wrap_result_serializer = True
        new_serializer_class = serializer_class.get_result_serializer_class()
        self.assertNotEqual(serializer_class, new_serializer_class)
        serializer = new_serializer_class(many=False)
        self.assertTrue(hasattr(serializer.instance, "result"))
        self.assertFalse(hasattr(serializer.instance, "results"))

    def test_no_wrap_serializer_class_many(self):
        serializer_class = testtools.create_serializer_class(
            fields_config=self.fields_config, serializer_base_classes=self.base_classes
        )
        serializer_class._wrap_result_serializer = False
        new_serializer_class = serializer_class.get_result_serializer_class()
        self.assertEqual(new_serializer_class, serializer_class)

    def test_no_wrap_serializer_class_not_many(self):
        serializer_class = testtools.create_serializer_class(
            fields_config=self.fields_config, serializer_base_classes=self.base_classes
        )
        serializer_class._wrap_result_serializer = False
        new_serializer_class = serializer_class.get_result_serializer_class()
        self.assertEqual(new_serializer_class, serializer_class)


class ModelSerializerTestCase(TestCase):
    def test_build_standard_field_with_example(self):
        model_fields_config = {
            "name": db_fields.CharField(max_length=255, example="Thomas"),
            "age": db_fields.IntegerField(example=33),
        }

        class ExampleModelSerializer(serializers.ModelSerializer):
            class Meta:
                model = testtools.create_model_class(fields_config=model_fields_config)
                fields = ["name", "age"]

        serializer = ExampleModelSerializer()
        field, field_kwargs = serializer.build_standard_field(
            "name", model_fields_config["name"]
        )
        self.assertEqual(field, serializers.CharField)
        self.assertEqual(field_kwargs["example"], "Thomas")

        field, field_kwargs = serializer.build_standard_field(
            "age", model_fields_config["age"]
        )
        self.assertEqual(field, serializers.IntegerField)
        self.assertEqual(field_kwargs["example"], 33)

    def test_build_standard_field_with_no_example(self):
        model_fields_config = {
            "name": db_fields.CharField(max_length=255),
            "age": db_fields.IntegerField(),
        }

        class ExampleModelSerializer(serializers.ModelSerializer):
            class Meta:
                model = testtools.create_model_class(fields_config=model_fields_config)
                fields = ["name", "age"]

        serializer = ExampleModelSerializer()
        field, field_kwargs = serializer.build_standard_field(
            "name", model_fields_config["name"]
        )
        self.assertEqual(field, serializers.CharField)
        self.assertIsNotNone(field_kwargs["example"])

        field, field_kwargs = serializer.build_standard_field(
            "age", model_fields_config["age"]
        )


class DisplayNamedWritableFieldTestCase(TestCase):
    def setUp(self):
        self.choices = make_choices("COLOR", ((0, "RED", "Red"), (1, "BLUE", "Blue")))
        self.field = serializers.DisplayNameWritableField(
            choices=self.choices.get_choices()
        )

    def test_to_representation_success(self):
        representation = self.field.to_representation(0)
        self.assertEqual(representation, "Red")
        representation = self.field.to_representation(1)
        self.assertEqual(representation, "Blue")

    def test_to_internal_value_success(self):
        representation = self.field.to_internal_value("Red")
        self.assertEqual(representation, 0)
        representation = self.field.to_internal_value("Blue")
        self.assertEqual(representation, 1)

    def test_to_internal_value_validation_error_failure(self):
        try:
            self.field.to_internal_value("Tom")
        except Exception as e:
            self.assertEqual(type(e), serializers.ValidationError)
            self.assertEqual(str(e.detail[0]), '"Tom" is not valid choice.')
            self.assertEqual(e.detail[0].code, "invalid")
