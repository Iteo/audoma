from rest_framework.exceptions import ErrorDetail
from rest_framework.fields import CharField
from rest_framework.serializers import ValidationError
from rest_framework.test import APITestCase

from audoma.drf.fields import SerializerMethodField as AudomaSerializerMethodField


class SerializerMethodFieldTestCase(APITestCase):
    databases = "__all__"

    def test_create_without_field(self):
        field = AudomaSerializerMethodField()
        self.assertIsInstance(field, AudomaSerializerMethodField)
        self.assertIsNone(getattr(field, "field", None))

    def test_create_with_field(self):
        field = AudomaSerializerMethodField(
            field=CharField(max_length=255), writable=True
        )
        self.assertIsInstance(field, AudomaSerializerMethodField)
        self.assertIsNotNone(getattr(field, "field", None))
        self.assertIsInstance(field.field, CharField)

    def test_run_validation_valid_example(self):
        field = AudomaSerializerMethodField(
            field=CharField(max_length=255), writable=True
        )
        field.field_name = "test_field"
        self.assertEqual(field.run_validation("TestValue"), {"test_field": "TestValue"})
        self.assertEqual(field.run_validation(12), {"test_field": "12"})
        self.assertEqual(field.run_validation(21.37), {"test_field": "21.37"})

    def test_run_validation_invalid_example(self):
        field = AudomaSerializerMethodField(
            field=CharField(max_length=255), writable=True
        )
        try:
            field.run_validation("a" * 289)
        except ValidationError as e:
            self.assertEqual(
                e.detail[0],
                ErrorDetail(
                    "Ensure this field has no more than 255 characters.", "max_length"
                ),
            )

    def test_to_internal_value_success(self):
        field = AudomaSerializerMethodField(
            field=CharField(max_length=255), writable=True
        )
        field.field_name = "test_field"
        self.assertEqual(
            field.to_internal_value("TestValue"), {"test_field": "TestValue"}
        )
        self.assertEqual(field.to_internal_value(12), {"test_field": "12"})
        self.assertEqual(field.to_internal_value(21.37), {"test_field": "21.37"})

    def test_to_internal_value_fail_validation(self):
        field = AudomaSerializerMethodField(
            field=CharField(max_length=255), writable=True
        )
        try:
            field.to_internal_value("a" * 289)
        except ValidationError as e:
            self.assertEqual(
                e.detail[0],
                ErrorDetail(
                    "Ensure this field has no more than 255 characters.", "max_length"
                ),
            )

    def test_to_internal_value_fail_type(self):
        field = AudomaSerializerMethodField(
            field=CharField(max_length=255), writable=True
        )
        try:
            field.to_internal_value(object())
        except ValidationError as e:
            self.assertEqual(e.detail[0], ErrorDetail("Not a valid string.", "invalid"))

    def test_to_internal_value_raise_skipfield(self):
        field = AudomaSerializerMethodField(
            field=CharField(max_length=255), writable=True
        )
        try:
            field.to_internal_value(object())
        except ValidationError as e:
            self.assertEqual(e.detail[0], ErrorDetail("Not a valid string.", "invalid"))
