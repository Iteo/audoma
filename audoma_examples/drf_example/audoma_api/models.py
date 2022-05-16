import random
from itertools import cycle

from django.utils.functional import lazy

from audoma.choices import make_choices
from audoma.django.db import models


example_countries = cycle(["United States", "Canada", "France", "Poland", "Italy"])
example_cities = ["New York", "Athens", "Toronto", "Rome", "Tokyo", "Oslo"]


def get_countries():
    return next(example_countries)


def get_random_age():
    return random.randint(18, 80)


# Create your models here.
class Account(models.Model):

    ACCOUNT_TYPE = make_choices(
        "CHOICES",
        (
            (1, "FACEBOOK", "facebook"),
            (2, "GMAIL", "gmail"),
            (3, "OTHER", "other"),
        ),
    )
    username = models.CharField(max_length=255)
    first_name = models.CharField(max_length=225, example="Adam")
    last_name = models.CharField(max_length=255, example="Smith")
    # phone_number = models.PhoneNumberField(example="+123456789") - we can add our own example
    phone_number = models.PhoneNumberField(region="PL")  # generates localized example
    nationality = models.CharField(max_length=255, example=get_countries)
    city = models.CharField(
        max_length=255, example=lazy(lambda: random.choice(example_cities), str)
    )
    email = models.EmailField()
    bio = models.TextField()
    is_active = models.BooleanField()
    mac_adress = models.MACAddressField()
    ip_address = models.GenericIPAddressField()
    age = models.IntegerField()
    _float = models.FloatField()
    decimal = models.DecimalField(decimal_places=2, max_digits=10)
    duration = models.DurationField()
    account_type = models.IntegerField(choices=ACCOUNT_TYPE.get_choices())
    # json = models.JSONField()
    account_balance = models.MoneyField(
        max_digits=14, decimal_places=2, default_currency="PLN"
    )


class Auction(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.TextField()
    price = models.MoneyField(max_digits=14, decimal_places=2, default_currency="PLN")
    file_field = models.FileField()
    posted_at = models.DateTimeField()


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
