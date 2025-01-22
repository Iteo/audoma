import os

from django.apps import AppConfig


class HealthcareApiConfig(AppConfig):
    name = "healthcare_api"
    path = os.path.dirname(os.path.abspath(__file__))
