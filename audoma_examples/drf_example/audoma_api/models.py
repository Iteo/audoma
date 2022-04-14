import random
from itertools import cycle

from jsonfield import JSONField

from django.utils.functional import lazy

from audoma.choices import make_choices
from audoma.django.db import models
from audoma.django_modelfields import (
    MACAddressField,
    PhoneNumberField,
)


# Create your models here.
class ExampleModel(models.Model):

    EXAMPLE_CHOICES = make_choices(
        "CHOICES",
        (
            (1, "EX_1", "example 1"),
            (2, "EX_2", "example 2"),
            (3, "EX_3", "example 3"),
        ),
    )
    char_field = models.CharField(max_length=255)
    phone_number = PhoneNumberField()
    email = models.EmailField()
    url = models.URLField()
    boolean = models.BooleanField()
    nullboolean = models.BooleanField(null=True)
    mac_adress = MACAddressField()
    slug = models.SlugField()
    uuid = models.UUIDField()
    ip_address = models.GenericIPAddressField()
    integer = models.IntegerField()
    _float = models.FloatField()
    decimal = models.DecimalField(decimal_places=2, max_digits=10)
    datetime = models.DateTimeField()
    date = models.DateField()
    time = models.TimeField()
    duration = models.DurationField()
    choices = models.IntegerField(choices=EXAMPLE_CHOICES.get_choices())
    json = JSONField()
    money = models.MoneyField(decimal_places=2, max_digits=10)


example_countries = cycle(["United States", "Canada", "France", "Poland", "Italy"])
example_cities = ["New York", "Athens", "Toronto", "Rome", "Tokyo", "Oslo"]


def get_countries():
    return next(example_countries)


def get_random_age():
    return random.randint(18, 80)


class ExamplePerson(models.Model):
    first_name = models.CharField(max_length=225, example="Adam")
    last_name = models.CharField(max_length=255, example="Smith")
    age = models.IntegerField(example=get_random_age)
    email = models.EmailField(example="example_person@example.com")
    birth_country = models.CharField(max_length=255, example=get_countries)
    residence_city = models.CharField(
        max_length=255, example=lazy(lambda: random.choice(example_cities), str)
    )
    has_valid_account = models.BooleanField()
    ip_address = models.GenericIPAddressField()
    savings = models.MoneyField(max_digits=14, decimal_places=2, default_currency="PLN")


class ExampleFileModel(models.Model):
    file_field = models.FileField()
    name = models.CharField(max_length=255)
