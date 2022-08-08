from django.test import TestCase

from audoma.choices import make_choices
from audoma.django.db import fields as django_fields
from audoma.django.forms import MoneyField
from audoma.tests.testtools import create_model_class


class CurrencyFieldTestCase(TestCase):
    def create_currency_field_with_default_currency(self):
        field = django_fields.CurrencyField(default="PLN")
        self.assertEqual(field.example, "PLN")

    def create_currency_field_with_currency_choices(self):
        choices = make_choices("CURRENC", ((0, "PLN", "pln"), (1, "USD", "Usd")))

        field = django_fields.CurrencyField(choices=choices.get_choices())
        self.assertEqual(field.example, "PLN")

    def create_currency_field_without_default_currency_or_choices(self):
        field = django_fields.CurrencyField()
        self.assertEqual(field.example, "XYZ")


class MoneyFieldTestCase(TestCase):
    def setUp(self):
        self.field = django_fields.MoneyField(
            verbose_name="Product's price",
            name="price",
            max_digits=4,
        )
        self.model = create_model_class(fields_config={"price": self.field})

    def test_add_currency_field(self):
        self.field.add_currency_field(self.model, "currency")
        self.assertTrue(hasattr(self.model, "price"))
        self.assertIsInstance(self.field._currency_field, django_fields.CurrencyField)

    def test_formfield_no_kwargs(self):
        formfield = self.field.formfield()
        formfield._has_defaults = False
        self.assertIsInstance(formfield, MoneyField)
        self.assertEqual(formfield.decimal_places, self.field.decimal_places)
