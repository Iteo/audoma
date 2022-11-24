from healthcare_api import models as health_models
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from django.urls import reverse


class PatientViewsetTestCase(APITestCase):
    def setUp(self):
        # create patients
        super().setUp()
        self.user = User.objects.create(
            username="admin", password="passwd", is_staff=True
        )
        contact_data = health_models.ContactData.objects.create(
            **{
                "phone_number": "+48 123 456 123",
                "mobile": "+48 908 787 343",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Lasowice",
            }
        )
        for i in range(3):
            health_models.Patient.objects.create(
                name="z" + "z" * i,
                surname="a" + "a",
                contact_data=contact_data,
                height="189.00",
                weight=89.02,
            )

    def test_get_list_success(self):
        url = reverse("patient-list")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 3)

    def test_get_list_fail_auth(self):
        url = reverse("patient-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["errors"]["detail"],
            "Authentication credentials were not provided.",
        )

    def test_get_list_fail_not_admin_user(self):
        url = reverse("patient-list")
        user = User.objects.create(username="test", password="test", is_staff=False)
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        print(response.data["errors"]["detail"])
        self.assertEqual(
            response.data["errors"]["detail"],
            "You do not have permission to perform this action.",
        )

    def test_create_single_success(self):
        url = reverse("patient-list")
        self.client.force_authenticate(user=self.user)
        request_data = {
            "name": "TestPatient",
            "surname": "Testowy",
            "contact_data": {
                "phone_number": "+48123909834",
                "mobile": "+48123909834",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Lasowice",
            },
            "weight": 80.0,
            "height": "179.04",
        }
        response = self.client.post(url, request_data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, request_data)
