from collections import OrderedDict

from drf_example.v2_urls import router
from drf_spectacular.generators import SchemaGenerator
from healthcare_api import models as health_models
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from django.urls import reverse


class HealthcareAPITestMixin:
    databases = {"healthcare_api", "default"}


class SchemaTestCaseBase(HealthcareAPITestMixin, APITestCase):
    def setUp(self) -> None:
        super().setUp()
        patterns = router.urls
        generator = SchemaGenerator(patterns=patterns)
        self.schema = generator.get_schema(request=None, public=True)
        self.redoc_schemas = self.schema["components"]["schemas"]


class BasicTestCase(HealthcareAPITestMixin, APITestCase):
    def setUp(self):
        # create patients
        super().setUp()
        self.user = User.objects.create(
            username="admin", password="passwd", is_staff=True
        )
        self.non_staff_user = User.objects.create(
            username="anybody", password="passwd", is_staff=False
        )


class PatientViewsetTestCase(BasicTestCase):
    def setUp(self):
        # create patients
        super().setUp()
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
                surname="a" + "a" * i,
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
        self.client.force_authenticate(user=self.non_staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
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
                "phone_number": "+48 12 390 98 34",
                "mobile": "+48 12 390 98 34",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Lasowice",
            },
            "weight": 80.0,
            "height": "179.04",
        }
        response = self.client.post(url, request_data, format="json")
        request_data["contact_data"]["country"] = 1
        request_data["contact_data"] = OrderedDict(request_data["contact_data"])
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(response.data, request_data)

    def test_create_single_fail_invalid_or_missing_data(self):
        url = reverse("patient-list")
        self.client.force_authenticate(user=self.user)
        request_data = {
            "name": "TestPatient",
            "surname": "Testowy",
            "contact_data": {
                "phone_number": "+48 12 390 98 34",
                "mobile": "+48 12 390 98 34",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Lasowice",
            },
            "weight": 80.0,
            "height": "179.04",
        }
        request_data["weight"] = "testtestest"
        response = self.client.post(url, request_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.data, {"errors": {"weight": ["A valid number is required."]}}
        )

    def test_create_single_fail_auth(self):
        url = reverse("patient-list")
        request_data = {
            "name": "TestPatient",
            "surname": "Testowy",
            "contact_data": {
                "phone_number": "+48 12 390 98 34",
                "mobile": "+48 12 390 98 34",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Lasowice",
            },
            "weight": 80.0,
            "height": "179.04",
        }
        response = self.client.post(url, request_data, format="json")
        request_data["contact_data"]["country"] = 1
        request_data["contact_data"] = OrderedDict(request_data["contact_data"])
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["errors"]["detail"],
            "Authentication credentials were not provided.",
        )

    def test_create_single_fail_permission(self):
        url = reverse("patient-list")
        self.client.force_authenticate(user=self.non_staff_user)
        request_data = {
            "name": "TestPatient",
            "surname": "Testowy",
            "contact_data": {
                "phone_number": "+48 12 390 98 34",
                "mobile": "+48 12 390 98 34",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Lasowice",
            },
            "weight": 80.0,
            "height": "179.04",
        }
        response = self.client.post(url, request_data, format="json")
        request_data["contact_data"]["country"] = 1
        request_data["contact_data"] = OrderedDict(request_data["contact_data"])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["errors"]["detail"],
            "You do not have permission to perform this action.",
        )

    def test_create_bulk_success(self):
        url = reverse("patient-list")
        self.client.force_authenticate(user=self.user)
        request_data = [
            {
                "name": "TestPatient",
                "surname": "Testowy",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": 80.0,
                "height": "179.04",
            },
            {
                "name": "TestPatient2",
                "surname": "Testowy2",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": 83.0,
                "height": "171.04",
            },
        ]
        response = self.client.post(url, request_data, format="json")
        first_response_data = request_data[0]
        first_response_data["contact_data"]["country"] = 1
        first_response_data["contact_data"] = OrderedDict(
            first_response_data["contact_data"]
        )
        second_response_data = request_data[1]
        second_response_data["contact_data"]["country"] = 1
        second_response_data["contact_data"] = OrderedDict(
            second_response_data["contact_data"]
        )
        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response.data, list)
        self.assertDictEqual(response.data[0], first_response_data)
        self.assertDictEqual(response.data[1], second_response_data)

    def test_create_bulk_fail_wrong_or_missing_data(self):
        url = reverse("patient-list")
        self.client.force_authenticate(user=self.user)
        request_data = [
            {
                "name": "TestPatient",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": 80.0,
                "height": "179.04",
            },
            {
                "name": "TestPatient2",
                "surname": "Testowy2",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": "ZHD",
                "height": "171.04",
            },
        ]
        response = self.client.post(url, request_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response.data["errors"], list)
        self.assertDictEqual(
            response.data["errors"][0], {"surname": ["This field is required."]}
        )
        self.assertDictEqual(
            response.data["errors"][1], {"weight": ["A valid number is required."]}
        )

    def test_create_bulk_fail_no_auth(self):
        url = reverse("patient-list")
        request_data = [
            {
                "name": "TestPatient",
                "surname": "Testowy",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": 80.0,
                "height": "179.04",
            },
            {
                "name": "TestPatient2",
                "surname": "Testowy2",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": 83.0,
                "height": "171.04",
            },
        ]
        response = self.client.post(url, request_data, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["errors"]["detail"],
            "Authentication credentials were not provided.",
        )

    def test_create_bulk_fail_permission(self):
        url = reverse("patient-list")
        self.client.force_authenticate(user=self.non_staff_user)
        request_data = [
            {
                "name": "TestPatient",
                "surname": "Testowy",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": 80.0,
                "height": "179.04",
            },
            {
                "name": "TestPatient2",
                "surname": "Testowy2",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": 83.0,
                "height": "171.04",
            },
        ]
        response = self.client.post(url, request_data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["errors"]["detail"],
            "You do not have permission to perform this action.",
        )

    def test_partial_update_single_success(self):
        self.client.force_authenticate(user=self.user)
        instance = health_models.Patient.objects.get(surname="aa")
        url = reverse("patient-detail", kwargs={"pk": instance.id})
        response = self.client.patch(url, {"name": "ThisIsPartialUpdate"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "name": "ThisIsPartialUpdate",
                "surname": "aa",
                "contact_data": OrderedDict(
                    [
                        ("phone_number", "+48 12 345 61 23"),
                        ("mobile", "+48 908 787 343"),
                        ("country", 1),
                        ("city", "Lasowice"),
                    ]
                ),
                "weight": 89.02,
                "height": "189.00",
            },
        )

    def test_partial_update_single_fail_wrong_data(self):
        self.client.force_authenticate(user=self.user)
        instance = health_models.Patient.objects.get(surname="aa")
        url = reverse("patient-detail", kwargs={"pk": instance.id})
        response = self.client.patch(url, {"weight": "WRONG_DATA"})
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.data["errors"], {"weight": ["A valid number is required."]}
        )

    def test_partial_update_single_fail_auth(self):
        instance = health_models.Patient.objects.get(surname="aa")
        url = reverse("patient-detail", kwargs={"pk": instance.id})
        response = self.client.patch(url, {"name": "CorrectName"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["errors"]["detail"],
            "Authentication credentials were not provided.",
        )

    def test_partial_update_single_fail_permission(self):
        self.client.force_authenticate(user=self.non_staff_user)
        instance = health_models.Patient.objects.get(surname="aa")
        url = reverse("patient-detail", kwargs={"pk": instance.id})
        response = self.client.patch(url, {"name": "CorrectName"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["errors"]["detail"],
            "You do not have permission to perform this action.",
        )

    def test_update_single_success(self):
        self.client.force_authenticate(user=self.user)
        instance = health_models.Patient.objects.get(surname="aa")
        url = reverse("patient-detail", kwargs={"pk": instance.id})
        request_data = {
            "name": "TestPatient",
            "surname": "Testowy",
            "contact_data": {
                "phone_number": "+48 12 390 98 34",
                "mobile": "+48 12 390 98 34",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Lasowice",
            },
            "weight": 80.0,
            "height": "179.04",
        }
        response = self.client.put(url, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        request_data["contact_data"]["country"] = 1
        request_data["contact_data"] = OrderedDict(request_data["contact_data"])
        self.assertDictEqual(response.data, request_data)

    def test_update_single_fail_wrong_data(self):
        self.client.force_authenticate(user=self.user)
        instance = health_models.Patient.objects.get(surname="aa")
        url = reverse("patient-detail", kwargs={"pk": instance.id})
        request_data = {
            "name": "TestPatient",
            "surname": "Testowy",
            "contact_data": {
                "phone_number": "+48 12 390 98 34",
                "mobile": "+48 12 390 98 34",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Lasowice",
            },
            "weight": 80.0,
            "height": "179.04",
        }
        request_data["weight"] = "testtestest"
        response = self.client.put(url, request_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.data, {"errors": {"weight": ["A valid number is required."]}}
        )

    def test_update_single_fail_missing_data(self):
        self.client.force_authenticate(user=self.user)
        instance = health_models.Patient.objects.get(surname="aa")
        url = reverse("patient-detail", kwargs={"pk": instance.id})
        request_data = {
            "name": "TestPatient",
            "contact_data": {
                "phone_number": "+48 12 390 98 34",
                "mobile": "+48 12 390 98 34",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Lasowice",
            },
            "weight": 80.0,
            "height": "179.04",
        }
        response = self.client.put(url, request_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.data, {"errors": {"surname": ["This field is required."]}}
        )

    def test_bulk_update_success(self):
        url = reverse("patient-list")
        self.client.force_authenticate(user=self.user)
        data = health_models.Patient.objects.all()[:2]

        request_data = [
            {
                "pk": data[0].id,
                "name": "TestPatient",
                "surname": "Testowy",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": 80.0,
                "height": "179.04",
            },
            {
                "pk": data[1].id,
                "name": "TestPatient2",
                "surname": "Testowy2",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": 83.0,
                "height": "171.04",
            },
        ]
        response = self.client.put(url, request_data, format="json")
        temp = []
        for r in request_data:
            r.pop("pk")
            temp.append(r)
        request_data = temp
        first_response_data = OrderedDict(request_data[0])
        first_response_data["contact_data"]["country"] = 1
        first_response_data["contact_data"] = OrderedDict(
            first_response_data["contact_data"]
        )
        second_response_data = OrderedDict(request_data[1])
        second_response_data["contact_data"]["country"] = 1
        second_response_data["contact_data"] = OrderedDict(
            second_response_data["contact_data"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertDictEqual(response.data[0], first_response_data)
        self.assertDictEqual(response.data[1], second_response_data)

    def test_bulk_update_invalid_and_missing_data(self):
        url = reverse("patient-list")
        self.client.force_authenticate(user=self.user)
        data = health_models.Patient.objects.all()[:2]

        request_data = [
            {
                "pk": data[0].id,
                "name": "TestPatient",
                "surname": "Testowy",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": "asdfqwf",
                "height": "179.04",
            },
            {
                "pk": data[1].id,
                "surname": "Testowy2",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": 83.0,
                "height": "171.04",
            },
        ]
        response = self.client.put(url, request_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.data["errors"][1], {"name": ["This field is required."]}
        )
        self.assertDictEqual(
            response.data["errors"][0], {"weight": ["A valid number is required."]}
        )

    def test_bulk_update_fail_no_auth(self):
        url = reverse("patient-list")
        data = health_models.Patient.objects.all()[:2]

        request_data = [
            {
                "pk": data[0].id,
                "name": "TestPatient",
                "surname": "Testowy",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": "asdfqwf",
                "height": "179.04",
            },
            {
                "pk": data[1].id,
                "surname": "Testowy2",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": 83.0,
                "height": "171.04",
            },
        ]
        response = self.client.put(url, request_data, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["errors"]["detail"],
            "Authentication credentials were not provided.",
        )

    def test_bulk_update_fail_missing_permissions(self):
        url = reverse("patient-list")
        self.client.force_authenticate(user=self.non_staff_user)
        data = health_models.Patient.objects.all()[:2]

        request_data = [
            {
                "pk": data[0].id,
                "name": "TestPatient",
                "surname": "Testowy",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": "asdfqwf",
                "height": "179.04",
            },
            {
                "pk": data[1].id,
                "surname": "Testowy2",
                "contact_data": {
                    "phone_number": "+48 12 390 98 34",
                    "mobile": "+48 12 390 98 34",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": 83.0,
                "height": "171.04",
            },
        ]
        response = self.client.put(url, request_data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["errors"]["detail"],
            "You do not have permission to perform this action.",
        )

    def test_bulk_partial_update_success(self):
        url = reverse("patient-list")
        self.client.force_authenticate(user=self.user)
        data = health_models.Patient.objects.all()[:2]

        expected_response = [
            {
                "name": "TestPatient",
                "surname": d.surname,
                "contact_data": {
                    "phone_number": "+48 12 345 61 23",
                    "mobile": "+48 908 787 343",
                    "country": health_models.COUNTRY_CHOICES.PL,
                    "city": "Lasowice",
                },
                "weight": d.weight,
                "height": str(d.height),
            }
            for d in data
        ]
        response = self.client.patch(
            url,
            [
                {"pk": data[0].id, "name": "TestPatient"},
                {"pk": data[1].id, "name": "TestPatient"},
            ],
            format="json",
        )
        first_response_data = OrderedDict(expected_response[0])
        first_response_data["contact_data"]["country"] = 1
        first_response_data["contact_data"] = OrderedDict(
            first_response_data["contact_data"]
        )
        second_response_data = OrderedDict(expected_response[1])
        second_response_data["contact_data"]["country"] = 1
        second_response_data["contact_data"] = OrderedDict(
            second_response_data["contact_data"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertDictEqual(response.data[0], first_response_data)
        self.assertDictEqual(response.data[1], second_response_data)

    def test_bulk_partial_update_fail_invalid_data(self):
        url = reverse("patient-list")
        self.client.force_authenticate(user=self.user)
        data = health_models.Patient.objects.all()[:2]
        response = self.client.patch(
            url,
            [
                {"pk": data[0].id, "weight": "TestPatient"},
                {"pk": data[1].id, "weight": "TestPatient"},
            ],
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.data["errors"][0], {"weight": ["A valid number is required."]}
        )
        self.assertDictEqual(
            response.data["errors"][1], {"weight": ["A valid number is required."]}
        )

    def test_bulk_partial_update_fail_permission(self):
        url = reverse("patient-list")
        self.client.force_authenticate(user=self.non_staff_user)
        data = health_models.Patient.objects.all()[:2]
        response = self.client.patch(
            url,
            [
                {"pk": data[0].id, "weight": "TestPatient"},
                {"pk": data[1].id, "weight": "TestPatient"},
            ],
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["errors"]["detail"],
            "You do not have permission to perform this action.",
        )

    def test_bulk_partial_update_fail_no_auht(self):
        url = reverse("patient-list")
        data = health_models.Patient.objects.all()[:2]
        response = self.client.patch(
            url,
            [
                {"pk": data[0].id, "weight": "TestPatient"},
                {"pk": data[1].id, "weight": "TestPatient"},
            ],
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["errors"]["detail"],
            "Authentication credentials were not provided.",
        )

    # TODO - fix this befor launch
    # def test_get_files_success(self):
    #    patient = health_models.Patient.objects.get(id=1)
    #    files = health_models.PatientFiles.objects.create(patient=patient)
    #    entry = health_models.FileEntry.objects.create(
    #        title="SecretInformation",
    #        content="SecretContent",
    #        files=files
    #    )
    #    url = reverse("patient-get-files", kwargs={"pk": 1})
    #    self.client.force_authenticate(user=self.user)
    #    response = self.client.get(url)
    #    self.assertEqual(response.status_code, 200)
    #    self.maxDiff = None
    #    expected_response = {
    #        "patient": OrderedDict({
    #            "name": "z",
    #            "surname": "a",
    #            "contact_data": OrderedDict({
    #                "phone_number": "+48 123 456 123",
    #                "mobile": "+48 908 787 343",
    #                "country": health_models.COUNTRY_CHOICES.PL,
    #                "city": "Lasowice",
    #            }),
    #            "height": "189.00",
    #            "weight": 89.02
    #        }),
    #        "entries": OrderedDict({
    #            "created_at": entry.created_at,
    #            "modified_at": entry.modifed_at,
    #            "title": "SecretInformation",
    #            "content": "SecretContent"
    #        })
    #    }
    #    self.assertDictEqual(
    #        response.data, expected_response
    #    )

    def test_get_files_fail_not_existing_patient(self):
        url = reverse("patient-get-files", kwargs={"pk": 2137})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_files_fail_permission(self):
        patient = health_models.Patient.objects.get(id=1)
        health_models.PatientFiles.objects.create(patient=patient)
        url = reverse("patient-get-files", kwargs={"pk": 1})
        self.client.force_authenticate(user=self.non_staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["errors"]["detail"],
            "You do not have permission to perform this action.",
        )

    def test_get_files_fail_no_auth(self):
        url = reverse("patient-get-files", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["errors"]["detail"],
            "Authentication credentials were not provided.",
        )


class PatientViewsetSchemaTestCase(SchemaTestCaseBase):
    def test_get_list_path_schema(self):
        path_schema = self.schema["paths"]["/patient/"]["get"]
        self.assertEqual(
            path_schema["description"],
            "\n\n**Permissions:**\n`IsAuthenticated` & `IsAdminUser`\n+ `IsAuthenticated`: "
            + "*Allows access only to authenticated users.*\n+ `IsAdminUser`: "
            + "*Allows access only to admin users.*",
        )
        self.assertDictEqual(
            path_schema["responses"],
            {
                "200": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaginatedPatientReadList"
                            }
                        }
                    },
                    "description": "",
                }
            },
        )

    def test_get_list_response_schema(self):
        props = self.redoc_schemas["PatientRead"]["properties"]
        self.assertEqual(props["height"]["pattern"], "^\\d{0,4}(?:\\.\\d{0,2})?$")
        self.assertDictEqual(
            props["contact_data"], {"$ref": "#/components/schemas/ContactData"}
        )

    def test_contact_data_response_schema(self):
        props = self.redoc_schemas["ContactData"]["properties"]
        self.assertEqual(props["country"]["enum"], [1, 2])
        self.assertDictEqual(
            props["country"]["x-choices"], {"choices": {1: "Poland", 2: "Germany"}}
        )
        self.assertEqual(
            props["country"]["description"],
            "Filter by country \n * `1` - Poland\n * `2` - Germany\n",
        )
        self.assertEqual(props["phone_number"]["type"], "string")
        self.assertEqual(props["phone_number"]["format"], "tel")
        self.assertEqual(props["mobile"]["type"], "string")
        self.assertEqual(props["mobile"]["format"], "tel")


class DoctorViesetTestCase(BasicTestCase):
    def setUp(self):
        super().setUp()
        health_models.Specialization.objects.create(name="Pediatry")
        health_models.Specialization.objects.create(name="Radiology")
        health_models.Specialization.objects.create(name="Anesthesiology")
        self.specializations = health_models.Specialization.objects.all()
        contact_data = health_models.ContactData.objects.create(
            **{
                "phone_number": "+48 123 456 123",
                "mobile": "+48 908 787 343",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Lasowice",
            }
        )
        for i in range(3):
            salary = 3000.0 * i + 1000.0 * i
            doc = health_models.Doctor.objects.create(
                name="z" + "z" * i,
                surname="a" + "a" * i,
                contact_data=contact_data,
                salary=salary,
            )
            doc.specialization.add(self.specializations[i])
            doc.save()
        self.doctors = health_models.Doctor.objects.all()

    def test_get_list_success(self):
        url = reverse("doctor-list")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 3)
        results = response.data["results"]

        self.assertDictEqual(
            results[0]["specialization"][0], {"id": 1, "name": "Pediatry"}
        )
        self.assertDictEqual(
            results[1]["specialization"][0], {"id": 2, "name": "Radiology"}
        )
        self.assertDictEqual(
            results[2]["specialization"][0], {"id": 3, "name": "Anesthesiology"}
        )

    def test_get_list_no_auth(self):
        url = reverse("doctor-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["errors"]["detail"],
            "Authentication credentials were not provided.",
        )

    def test_get_list_lack_permissions(self):
        url = reverse("doctor-list")
        self.client.force_authenticate(user=self.non_staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["errors"]["detail"],
            "You do not have permission to perform this action.",
        )

    def test_create_doctor_success(self):
        url = reverse("doctor-list")
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "TeestDoctor",
            "surname": "Creepy",
            "contact_data": {
                "phone_number": "+48 455 123 432",
                "mobile": "+48 455 123 432",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Gliwice",
            },
            "salary": "5000.00",
            "specialization": [1, 2],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["specialization"], [1, 2])

    def test_create_doctor_failure_missing_data(self):
        url = reverse("doctor-list")
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "TeestDoctor",
            "surname": "Creepy",
            "contact_data": {
                "phone_number": "+48 455 123 432",
                "mobile": "+48 455 123 432",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Gliwice",
            },
            "specialization": [1, 2],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.data, {"errors": {"salary": ["This field is required."]}}
        )

    def test_create_doctor_failure_wrong_data(self):
        url = reverse("doctor-list")
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "TeestDoctor",
            "surname": "Creepy",
            "contact_data": {
                "phone_number": "+48 455 123 432",
                "mobile": "+48 455 123 432",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Gliwice",
            },
            "salary": "TEST",
            "specialization": [1, 2],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.data, {"errors": {"salary": ["A valid number is required."]}}
        )

    def test_create_doctor_failure_no_auth(self):
        url = reverse("doctor-list")
        data = {
            "name": "TeestDoctor",
            "surname": "Creepy",
            "contact_data": {
                "phone_number": "+48 455 123 432",
                "mobile": "+48 455 123 432",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Gliwice",
            },
            "specialization": [1, 2],
            "salary": "5000.00",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["errors"]["detail"],
            "Authentication credentials were not provided.",
        )

    def test_create_doctor_failure_missing_permissions(self):
        url = reverse("doctor-list")
        self.client.force_authenticate(user=self.non_staff_user)
        data = {
            "name": "TeestDoctor",
            "surname": "Creepy",
            "contact_data": {
                "phone_number": "+48 455 123 432",
                "mobile": "+48 455 123 432",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Gliwice",
            },
            "salary": "5000.00",
            "specialization": [1, 2],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["errors"]["detail"],
            "You do not have permission to perform this action.",
        )

    def test_update_doctor_success(self):
        url = reverse("doctor-detail", kwargs={"pk": 1})
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "TeestDoctor",
            "surname": "Creepy",
            "contact_data": {
                "phone_number": "+48 455 123 432",
                "mobile": "+48 455 123 432",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Gliwice",
            },
            "salary": "5000.00",
            "specialization": [1, 2],
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        data["contact_data"] = OrderedDict(data["contact_data"])
        self.assertDictEqual(response.data, data)

    def test_update_doctor_fail_missing_data(self):
        url = reverse("doctor-detail", kwargs={"pk": 1})
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "TeestDoctor",
            "surname": "Creepy",
            "contact_data": {
                "phone_number": "+48 455 123 432",
                "mobile": "+48 455 123 432",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Gliwice",
            },
            "specialization": [1, 2],
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.data, {"errors": {"salary": ["This field is required."]}}
        )

    def test_update_doctor_fail_wrong_data(self):
        url = reverse("doctor-detail", kwargs={"pk": 1})
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "TeestDoctor",
            "surname": "Creepy",
            "contact_data": {
                "phone_number": "+48 455 123 432",
                "mobile": "+48 455 123 432",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Gliwice",
            },
            "salary": "TEST",
            "specialization": [1, 2],
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.data, {"errors": {"salary": ["A valid number is required."]}}
        )

    def test_partial_update_doctor_success(self):
        url = reverse("doctor-detail", kwargs={"pk": 1})
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "TeestDoctor",
            "surname": "Creepy",
            "contact_data": {
                "phone_number": "+48 12 345 61 23",
                "mobile": "+48 908 787 343",
                "country": health_models.COUNTRY_CHOICES.PL,
                "city": "Lasowice",
            },
            "salary": "0.00",
            "specialization": [1],
        }
        response = self.client.patch(
            url,
            {
                "name": "TeestDoctor",
                "surname": "Creepy",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data["contact_data"] = OrderedDict(data["contact_data"])
        self.assertDictEqual(response.data, data)

    def test_partial_update_doctor_failure_wrong_data(self):
        url = reverse("doctor-detail", kwargs={"pk": 1})
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            url,
            {
                "salary": "Z@#!@FASD",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.data, {"errors": {"salary": ["A valid number is required."]}}
        )

    def test_partial_update_fail_no_auth(self):
        url = reverse("doctor-detail", kwargs={"pk": 1})
        response = self.client.patch(
            url,
            {
                "salary": "5000.0",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["errors"]["detail"],
            "Authentication credentials were not provided.",
        )

    def test_partial_update_fail_no_permissions(self):
        url = reverse("doctor-detail", kwargs={"pk": 1})
        self.client.force_authenticate(user=self.non_staff_user)
        response = self.client.patch(
            url,
            {
                "salary": "5000.0",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["errors"]["detail"],
            "You do not have permission to perform this action.",
        )
