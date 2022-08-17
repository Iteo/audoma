from rest_framework.exceptions import (
    NotFound,
    ValidationError,
)
from rest_framework.test import DjangoRequestFactory

from django.db.models import fields
from django.test import TestCase

from audoma.drf.mixins import (  # BulkUpdateModelMixin,
    ActionModelMixin,
    BulkCreateModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from audoma.drf.serializers import (
    BulkSerializerMixin,
    ModelSerializer,
)
from audoma.drf.viewsets import GenericViewSet
from audoma.tests.testtools import (
    create_basic_view,
    create_model_class,
    create_model_serializer_class,
)


class CommonMixinTestCase(TestCase):
    view_baseclasses = None

    def setUp(self):
        fields_config = {
            "name": fields.CharField(max_length=255),
            "age": fields.IntegerField(),
        }
        self.model = create_model_class(fields_config=fields_config)
        self.serializer_class = create_model_serializer_class(
            meta_model=self.model, meta_fields=["name", "age"]
        )
        self.view = create_basic_view(
            view_baseclasses=self.view_baseclasses,
            view_properties={"serializer_class": self.serializer_class},
        )
        self.view.format_kwarg = "json"
        self.factory = DjangoRequestFactory()


class ActionModelMixinTestCase(CommonMixinTestCase):

    view_baseclasses = (ActionModelMixin, GenericViewSet)

    def test_put_perform_action_with_instance_success(self):
        data = {"name": "John", "age": 47}
        instance = self.model(**data)
        request = self.factory.put("/example")
        request.data = data
        self.view.action = "create"
        self.view.request = request
        response = self.view.perform_action(
            request, instance=instance, success_status=201
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, data)

    def test_post_perform_action_without_instance(self):
        data = {"name": "John", "age": 47}
        request = self.factory.post("/example")
        request.data = data
        self.view.action = "create"
        self.view.request = request
        response = self.view.perform_action(request, success_status=201)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, data)

    def test_retrieve_instance_success(self):
        def get_object():
            return self.model(name="name", age=21)

        self.view.get_object = get_object
        request = self.factory.post("/example")
        self.view.action = "retrieve"
        self.view.request = request
        response = self.view.retrieve_instance(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"name": "name", "age": 21})

    def test_retrieve_instance_failure(self):
        def get_object():
            return

        self.view.get_object = get_object
        request = self.factory.post("/example")
        self.view.action = "retrieve"
        self.view.request = request
        try:
            self.view.retrieve_instance(request)
        except Exception as e:
            self.assertIsInstance(e, AssertionError)

    def test_get_success_headers_success(self):
        headers = self.view.get_success_headers(data={"url": "/header/test/"})
        self.assertEqual(headers, {"Location": "/header/test/"})

    def test_get_success_headers_failure(self):
        try:
            self.view.get_success_headers({})
        except Exception as e:
            self.assertIsInstance(e, KeyError)


class CreateModelMixinTestCase(CommonMixinTestCase):

    view_baseclasses = (CreateModelMixin, GenericViewSet)

    def test_create_success(self):
        data = {"name": "John", "age": 47}
        request = self.factory.post("/example")
        request.data = data
        self.view.action = "create"
        self.view.request = request
        response = self.view.create(request, success_status=201)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, data)

    def test_create_failure_missing_data(self):
        data = {
            "name": "John",
        }
        request = self.factory.post("/example")
        request.data = data
        self.view.action = "create"
        self.view.request = request
        try:
            self.view.create(request, success_status=201)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)
            self.assertEqual(e.detail["age"][0].code, "required")

    def test_create_failure_incorrect_data(self):
        data = {"name": "Test", "age": "THISISNOTANUMBER"}
        request = self.factory.post("/example")
        request.data = data
        self.view.action = "create"
        self.view.request = request
        try:
            self.view.create(request, success_status=201)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)
            self.assertEqual(e.detail["age"][0].code, "invalid")


class ListModelTestCase(CommonMixinTestCase):
    view_baseclasses = (ListModelMixin, GenericViewSet)

    def setUp(self):
        super().setUp()

        def get_queryset():
            return self.model.objects.none()

        self.view.get_queryset = get_queryset

    def test_list_no_message_success(self):
        request = self.factory.get("/example")
        request.query_params = {"page": 1}
        self.view.action = "list"
        self.view.request = request
        response = self.view.list(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["next"], None)
        self.assertEqual(response.data["previous"], None)
        self.assertEqual(response.data["results"], [])
        self.assertEqual(response.data["message"], None)

    def test_list_with_message_success(self):
        def get_list_message():
            return "Important list message"

        self.view.get_list_message = get_list_message

        request = self.factory.get("/example")
        request.query_params = {"page": 1}
        self.view.action = "list"
        self.view.request = request
        response = self.view.list(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["next"], None)
        self.assertEqual(response.data["previous"], None)
        self.assertEqual(response.data["results"], [])
        self.assertEqual(response.data["message"], "Important list message")

    def test_list_with_none_page_failure(self):
        request = self.factory.get("/example")
        request.query_params = {"page": None}
        self.view.action = "list"
        self.view.request = request
        try:
            self.view.list(request)
        except Exception as e:
            self.assertEqual(type(e), NotFound)
            self.assertEqual(e.detail, "Invalid page.")


class RetrieveModelMixinTestCase(CommonMixinTestCase):

    view_baseclasses = (RetrieveModelMixin, GenericViewSet)

    def setUp(self):
        super().setUp()

        def get_object():
            return self.model(name="name", age=21)

        self.view.get_object = get_object

    def test_retrieve_success(self):
        request = self.factory.post("/example")
        self.view.action = "retrieve"
        self.view.request = request
        response = self.view.retrieve(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"name": "name", "age": 21})


class UpdateModelMixinTestCase(CommonMixinTestCase):
    view_baseclasses = (UpdateModelMixin, GenericViewSet)

    def setUp(self):
        super().setUp()

        def get_object():
            return self.model(name="name", age=21)

        self.view.get_object = get_object

    def test_update_full_success(self):
        data = {"name": "John", "age": 47}
        request = self.factory.put("/example")
        request.data = data
        self.view.request = request
        self.view.action = "update"
        response = self.view.update(request, partial=False)
        response_data = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["name"], "John")
        self.assertEqual(response_data["age"], 47)

    def test_update_partial_success(self):
        data = {"age": 47}
        request = self.factory.patch("/example")
        request.data = data
        self.view.request = request
        self.view.action = "update"
        response = self.view.update(request, partial=True)
        response_data = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["age"], 47)


class DestroyModelMixinTestCase(CommonMixinTestCase):

    view_baseclasses = (DestroyModelMixin, GenericViewSet)

    def setUp(self):
        super().setUp()

        def get_object():
            instance = self.model(id=1, name="name", age=21)

            def delete():
                return True

            instance.delete = delete
            return instance

        self.view.get_object = get_object

    def test_destroy_success(self):
        request = self.factory.delete("/example")
        request.data = {"id": 1}
        self.view.request = request
        self.view.action = "destroy"
        response = self.view.destroy(request)
        self.assertEqual(response.status_code, 204)

    # TODO - add tests to invoke validation error


class BulkCreateModelMixinTestCase(CommonMixinTestCase):

    view_baseclasses = (BulkCreateModelMixin, GenericViewSet)

    def setUp(self):
        super().setUp()

        self.bulk_serializer_class = create_model_serializer_class(
            meta_model=self.model,
            meta_fields=["name", "age"],
            serializer_base_classes=(BulkSerializerMixin, ModelSerializer),
        )
        self.view.serializer_class = self.bulk_serializer_class

    def test_create_not_bulk_success(self):
        data = {"name": "John", "age": 47}

        def save(me):
            me.instance = self.model(id=1, name=data["name"], age=data["age"])
            return me.instance

        self.bulk_serializer_class.save = save
        self.view.serializer_class = self.bulk_serializer_class

        request = self.factory.post("/example")
        request.data = data
        self.view.action = "create"
        self.view.request = request
        response = self.view.create(request, success_status=201)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, data)

    # TODO - fix this test
    # def test_create_is_bulk_success(self):
    #     data = [{
    #         "name": "Greg",
    #         "age": 22
    #     },{
    #         "name": "John",
    #         "age": 47
    #     }]
    #     def save(me):
    #         objs = []
    #         for x, d in enumerate(data):
    #             objs.append(self.model(id=x, name=d["name"], age=d["age"]))
    #         me.instance = objs
    #         return objs
    #
    #     self.bulk_serializer_class.save = save
    #     self.view.serializer_class = self.bulk_serializer_class
    #     request = self.factory.post("/example")
    #     request.data = data
    #     self.view.action = "create"
    #     self.view.request = request
    #     response = self.view.create(
    #         request, success_status=201
    #     )
    #     self.assertEqual(response.status_code, 201)
    #     print(response.data)
    #     raise ValueError


# TODO - tests for BulkUpdate
