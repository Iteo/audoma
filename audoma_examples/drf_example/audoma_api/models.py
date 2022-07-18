import random
from itertools import cycle

from django.utils.functional import lazy

from audoma.choices import make_choices
from audoma.django.db import models


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
    phone_number = models.PhoneNumberField()
    phone_number_example = models.PhoneNumberField(example="+123456789")
    email = models.EmailField()
    text_field = models.TextField()
    url = models.URLField()
    boolean = models.BooleanField()
    nullboolean = models.BooleanField(null=True)
    mac_adress = models.MACAddressField()
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
    json = models.JSONField()
    money = models.MoneyField(decimal_places=2, max_digits=10)


example_countries = cycle(["United States", "Canada", "France", "Poland", "Italy"])
example_cities = ["New York", "Athens", "Toronto", "Rome", "Tokyo", "Oslo"]


def get_countries():
    return next(example_countries)


def get_random_age():
    return random.randint(18, 80)


class Country(models.Model):
    name = models.CharField(max_length=225, example=get_countries)


class ExamplePerson(models.Model):
    first_name = models.CharField(max_length=225, example="Adam")
    last_name = models.CharField(max_length=255, example="Smith")
    age = models.IntegerField(example=get_random_age)
    email = models.EmailField(example="example_person@example.com")
    birth_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    residence_city = models.CharField(
        max_length=255, example=lazy(lambda: random.choice(example_cities), str)
    )
    has_valid_account = models.BooleanField()
    ip_address = models.GenericIPAddressField()
    savings = models.MoneyField(max_digits=14, decimal_places=2, default_currency="PLN")
    phone_number = models.PhoneNumberField(region="IT")


class ExampleFileModel(models.Model):
    file_field = models.FileField()
    name = models.CharField(max_length=255)


class Manufacturer(models.Model):
    name = models.CharField(max_length=255)
    slug_name = models.SlugField()


class Car(models.Model):

    CAR_BODY_TYPES = make_choices(
        "BODY_TYPES",
        (
            (1, "SEDAN", "Sedan"),
            (2, "COUPE", "Coupe"),
            (3, "HATCHBACK", "Hatchback"),
            (4, "PICKUP", "Pickup Truck"),
        ),
    )

    ENGINE_TYPES = make_choices(
        "ENGINE_TYPES",
        (
            (1, "PETROL", "Petrol"),
            (2, "DIESEL", "Diesel"),
            (3, "ELECTRIC", "Electric"),
            (4, "HYBRID", "Hybrid"),
        ),
    )

    name = models.CharField(max_length=255)
    body_type = models.IntegerField(choices=CAR_BODY_TYPES.get_choices())

    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    engine_size = models.FloatField()
    engine_type = models.IntegerField(choices=ENGINE_TYPES.get_choices())
