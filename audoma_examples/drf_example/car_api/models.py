from audoma.choices import make_choices
from audoma.django.db import models


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
    created_by = models.ForeignKey(
        "django.contrib.auth.models.User", on_delete=models.CASCADE
    )

    # TODO - consider creatng more sensible function
    def is_sedan(self):
        return self.body_type is self.CAR_BODY_TYPES.SEDAN


class Salesman(models.Model):
    user = models.ForeignKey(
        "django.contrib.auth.models.User", on_delete=models.CASCADE
    )
    phone = models.PhoneNumberField(region="PL")

    @property
    def name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def rented_cars_number(self):
        return CarRent.objects.filter(rented_by=self).count()


class Customer(models.Model):

    user = models.ForeignKey(
        "django.contrib.auth.models.User", on_delete=models.CASCADE
    )
    phone = models.PhoneNumberField(region="PL")

    @property
    def name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def borrowed_cars_number(self):
        return CarRent.objects.filter(customer=self).count()


class CarRent(models.Model):

    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    rent_start = models.DateTimeField(auto_now_add=True)
    rent_end = models.DateTimeField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rented_by = models.ForeignKey(Salesman, on_delete=models.CASCADE)
