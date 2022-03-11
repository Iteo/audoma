from jsonfield import JSONField

from django.db import models

from audoma.choices import make_choices
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
