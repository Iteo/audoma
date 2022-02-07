from rest_framework.fields import *
from django.core import validators
from rest_framework import fields
from django.utils.functional import lazy
from audoma.drf.mixins import ExampleMixin
import exrex
from phonenumber_field import serializerfields

import random
import uuid


class DecimalField(ExampleMixin, fields.DecimalField):
    class Meta:
        swagger_schema_fields = {
            "example": lazy(lambda: "%.2f" % (random.random() * random.randint(1, 1000)), str)()
        }


class UUIDField(ExampleMixin, fields.UUIDField):
    class Meta:
        swagger_schema_fields = {
            "example": lazy(lambda: str(uuid.uuid4()), str)()
        }


class IntegerField(ExampleMixin, fields.IntegerField):
    class Meta:
        swagger_schema_fields = {
            "example": lazy(lambda: random.randint(1, 1000), int)()
        }


class FloatField(ExampleMixin, fields.FloatField):
    class Meta:
        swagger_schema_fields = {
            "example": lazy(lambda: (random.random() * random.randint(1, 1000)), float)()
        }


class RegexField(ExampleMixin, fields.RegexField):
   
    def __init__(self, regex, **kwargs):
        if 'example' not in kwargs: 
            kwargs['example'] =  lazy(lambda: str(exrex.getone(regex)), str)()
        super().__init__(regex, **kwargs)
        
        
class MACAddressField(ExampleMixin, fields.CharField):
    
    def __init__(self, **kwargs):
        self.regex = "^([0-9A-F]{2}:){5}([0-9A-F]{2})|([0-9A-F]{2}-){5}([0-9A-F]{2})$"
        self.validarors = [validators.RegexValidator(self.regex)]
        if 'example' not in kwargs: 
            kwargs['example'] =  lazy(lambda: str(exrex.getone(self.regex)), str)()
        super().__init__(**kwargs) 
    

class DateField(ExampleMixin, fields.DateField):
    pass


class TimeField(ExampleMixin, fields.TimeField):
    pass


class IPAddressField(ExampleMixin, fields.IPAddressField):
    
    class Meta:
        swagger_schema_fields = {
            "example": lazy(lambda: str(exrex.getone("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")), str)()
        }


class PhoneNumberField(ExampleMixin, serializerfields.PhoneNumberField):
    
    class Meta:
        swagger_schema_fields = {
            "example": lazy(lambda: str("+1 8888888822"), str)()
        }