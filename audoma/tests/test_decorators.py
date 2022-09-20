from rest_framework.exceptions import (
    APIException,
    MethodNotAllowed,
    PermissionDenied,
)
from rest_framework.serializers import Serializer
from rest_framework.test import APIRequestFactory

from django.core.exceptions import ImproperlyConfigured
from django.test import (
    TestCase,
    override_settings,
)

from audoma.decorators import (
    AudomaActionException,
    audoma_action,
)
from audoma.drf import fields as audoma_fields
from audoma.tests.testtools import (
    create_serializer_class,
    create_view_with_custom_audoma_action,
)


class AudomaActionTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()
        serializer_base_classes = [Serializer]
        fields_config = {
            "firstname": audoma_fields.CharField(max_length=255),
            "lastname": audoma_fields.CharField(max_length=255),
            "age": audoma_fields.IntegerField(),
        }
        self.example_collect_serializer = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=serializer_base_classes
        )
        self.example_result_serializer = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=serializer_base_classes
        )
        self.request_data = {"firstname": "John", "lastname": "DOG", "age": 45}

    @override_settings(DEBUG=False)
    def test_improperly_configured_audoma_action_decorator(self):
        try:
            audoma_action(
                collectors={"post": self.example_collect_serializer},
                results={"201": self.example_result_serializer},
                methods=["GET"],
                detail=True,
            )
        except ImproperlyConfigured as e:
            self.assertEqual(
                str(e),
                "There should be no collectors defined if there are not create/update requests accepted.",
            )

    def test_audoma_action_with_wrong_clas_passed_to_errors(self):
        class NotAnException:
            ...

        error = NotAnException

        try:
            audoma_action(
                collectors={"post": self.example_collect_serializer},
                results={"201": self.example_result_serializer},
                errors=[error],
                methods=["POST"],
                detail=False,
            )
        except ImproperlyConfigured as e:
            self.assertEqual(
                str(e),
                f"Something that is not an Exception instance or class has been passed \
                        to audoma_action errors list. The value which caused exception: {error}",
            )

    def test_audoma_action_multiple_exception_definitions(self):
        error = ValueError

        try:
            audoma_action(
                collectors={"post": self.example_collect_serializer},
                results={"201": self.example_result_serializer},
                errors=[error, error("Some Message")],
                methods=["POST"],
                detail=False,
            )
        except ImproperlyConfigured as e:
            self.assertEqual(
                str(e),
                f"Exception has been passed multiple times as an instance and as type, \
                        exception type: {error}",
            )

    def test_properly_defined_audoma_action(self):
        action = audoma_action(
            collectors={"post": self.example_collect_serializer},
            results={"201": self.example_result_serializer},
            methods=["POST"],
            detail=False,
        )
        self.assertEqual(type(action), audoma_action)

    def test_audoma_action_return_defined_response(self):
        request = self.factory.post("/custom_action/")
        request.data = self.request_data
        view = create_view_with_custom_audoma_action(
            request=request,
            action_kwargs={
                "collectors": {"post": self.example_collect_serializer},
                "results": {201: self.example_result_serializer},
                "methods": ["POST"],
                "detail": False,
            },
            returnables=(self.request_data, 201),
        )
        view.method = "post"
        view.format_kwarg = "json"
        view.request = request
        view.action = "custom_action"
        response = view.custom_action(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data, {"firstname": "John", "lastname": "DOG", "age": 45}
        )

    def test_audoma_action_return_undefined_response(self):
        request = self.factory.get("/custom_action/")
        fields_config = {"company_name": audoma_fields.CharField(max_length=255)}
        serializer_class = create_serializer_class(
            fields_config=fields_config, serializer_base_classes=[Serializer]
        )

        view = create_view_with_custom_audoma_action(
            request=request,
            action_kwargs={
                "collectors": {"post": self.example_collect_serializer},
                "results": {201: self.example_result_serializer},
                "methods": [
                    "POST",
                ],
                "detail": False,
            },
            returnables=({"company_name": "Lenovo"}, 200),
            view_properties={"serializer_class": serializer_class},
        )
        view.method = "get"
        view.format_kwarg = "json"
        view.request = request
        view.action = "retrieve"
        response = view.custom_action(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"company_name": "Lenovo"})

    def test_audoma_action_default_collector_fallback(self):
        request = self.factory.post("/custom_action/")
        request.data = self.request_data
        view = create_view_with_custom_audoma_action(
            request=request,
            action_kwargs={
                "results": {201: self.example_result_serializer},
                "methods": ["POST"],
                "detail": False,
            },
            returnables=(self.request_data, 201),
            view_properties={"serializer_class": self.example_collect_serializer},
        )
        view.method = "post"
        view.format_kwarg = "json"
        view.request = request
        view.action = "custom_action"
        response = view.custom_action(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data, {"firstname": "John", "lastname": "DOG", "age": 45}
        )

    def test_audoma_action_process_defined_exception(self):
        request = self.factory.post("/custom_action/")
        request.data = self.request_data
        view = create_view_with_custom_audoma_action(
            request=request,
            action_kwargs={
                "results": {201: self.example_result_serializer},
                "methods": ["POST"],
                "detail": False,
                "errors": [PermissionDenied("You are not allowed")],
            },
            returnables=(self.request_data, 201),
            view_properties={"serializer_class": self.example_collect_serializer},
            raiseable=PermissionDenied("You are not allowed"),
            raise_exception=True,
        )
        view.method = "post"
        view.request = request
        view.format_kwarg = "json"
        view.action = "custom_action"
        try:
            view.custom_action(request)
        except Exception as e:
            self.assertEqual(type(e), PermissionDenied)
            self.assertEqual(e.detail, "You are not allowed")
            self.assertEqual(e.status_code, 403)

    @override_settings(DEBUG=True)
    def test_audoma_action_process_undefined_exception(self):
        request = self.factory.post("/custom_action/")
        request.data = self.request_data
        view = create_view_with_custom_audoma_action(
            request=request,
            action_kwargs={
                "results": {200: self.example_result_serializer},
                "methods": ["GET"],
                "detail": False,
                "errors": [PermissionDenied("You are not allowed")],
            },
            returnables=(self.request_data, 200),
            view_properties={"serializer_class": self.example_collect_serializer},
            raiseable=MethodNotAllowed("POST"),
            raise_exception=True,
        )
        view.method = "post"
        view.request = request
        view.format_kwarg = "json"
        view.action = "custom_action"
        view.format_kwarg = "json"
        try:
            view.custom_action(request)
        except Exception as e:
            self.assertEqual(type(e), AudomaActionException)
            self.assertEqual(
                str(e),
                f"There is no class or instance of {MethodNotAllowed} \
                    defined in audoma_action errors.",
            )

    @override_settings(DEBUG=True)
    def test_audoma_action_process_different_content_exception(self):
        request = self.factory.post("/custom_action/")
        request.data = self.request_data

        class CustomException(APIException):
            default_detail = "This does not seem to work"

        raisable = CustomException("Something else happens")
        view = create_view_with_custom_audoma_action(
            request=request,
            action_kwargs={
                "results": {200: self.example_result_serializer},
                "methods": ["GET"],
                "detail": False,
                "errors": [CustomException("Something happens")],
            },
            returnables=(self.request_data, 200),
            view_properties={"serializer_class": self.example_collect_serializer},
            raiseable=raisable,
            raise_exception=True,
        )
        view.method = "post"
        view.request = request
        view.format_kwarg = "json"
        view.action = "custom_action"
        try:
            view.custom_action(request)
        except Exception as e:
            self.assertEqual(type(e), AudomaActionException)
            self.assertEqual(
                str(e),
                f"Raised error: {raisable} has not been \
                        defined in audoma_action errors.",
            )

    def test_audoma_action_many_param_true(self):
        request = self.factory.post("/custom_action/")
        request.data = [self.request_data]

        view = create_view_with_custom_audoma_action(
            request=request,
            action_kwargs={
                "results": {200: self.example_result_serializer},
                "methods": ["GET"],
                "detail": False,
                "many": True,
            },
            returnables=(
                [
                    self.request_data,
                ],
                200,
            ),
            view_properties={"serializer_class": self.example_collect_serializer},
        )
        view.method = "post"
        view.request = request
        view.format_kwarg = "json"
        view.action = "custom_action"
        response = view.custom_action(request)
        self.assertIsInstance(response.data, list)
