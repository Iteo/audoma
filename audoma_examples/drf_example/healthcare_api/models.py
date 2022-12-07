from django.contrib.postgres import fields as psql_fields

from audoma.choices import make_choices
from audoma.django.db import models


COUNTRY_CHOICES = make_choices(
    "COUNTRIES",
    ((1, "PL", "Poland"), (2, "DE", "Germany")),
)


class ContactData(models.Model):

    phone_number = models.PhoneNumberField(region="PL")
    mobile = models.PhoneNumberField(region="PL")

    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES.get_choices())
    city = models.CharField(max_length=200)


class Person(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    contact_data = models.ForeignKey(ContactData, on_delete=models.CASCADE)


class Specialization(models.Model):
    name = models.CharField(max_length=255)


class Doctor(Person):
    specialization = models.ManyToManyField(Specialization)
    salary = models.MoneyField(decimal_places=2, max_digits=10, default_currency="PLN")


class Patient(Person):
    weight = models.FloatField()
    height = models.DecimalField(decimal_places=2, max_digits=6)


class PatientFiles(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    @property
    def entries(self):
        return FileEntry.objects.filter(files=self)


class FileEntry(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modifed_at = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=200)
    content = models.TextField()
    files = models.ForeignKey(PatientFiles, on_delete=models.CASCADE)


class Prescription(models.Model):

    issued_by = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    issued_for = models.ForeignKey(Patient, on_delete=models.CASCADE)

    drugs = psql_fields.ArrayField(psql_fields.HStoreField())

    usable_in = psql_fields.DateRangeField()
    issued_in = psql_fields.CICharField(max_length=255)
    is_valid = models.BooleanField(default=True)
