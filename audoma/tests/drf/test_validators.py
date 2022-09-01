from rest_framework.exceptions import ValidationError

from django.test import TestCase

from audoma.drf.validators import ExclusiveFieldsValidator


class ExclusiveFieldsValidatorTestCase(TestCase):
    def setUp(self):
        self.validator = ExclusiveFieldsValidator(
            fields=["name", "company_name"],
            message="Fields: {field_names} are mutually exclusive",
            required=True,
            message_required="At least one of the fields: {field_names} is required",
        )

    def test_call_none_in_data(self):
        try:
            self.validator(data={"age": 245})
        except Exception as e:
            self.assertEqual(type(e), ValidationError)
            self.assertEqual(
                str(e.detail[0]),
                "At least one of the fields: name, company_name is required",
            )

    def test_call_all_in_data(self):
        try:
            self.validator(data={"name": "Test", "company_name": "Test"})
        except Exception as e:
            self.assertEqual(type(e), ValidationError)
            self.assertEqual(
                str(e.detail[0]), "Fields: name, company_name are mutually exclusive"
            )

    def test_call_one_in_data(self):
        try:
            val_response = self.validator(data={"name": "Test"})
        except Exception as e:
            raise e
        else:
            self.assertIsNone(val_response)
