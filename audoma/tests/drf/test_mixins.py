from typing import OrderedDict

from rest_framework.exceptions import (
    NotFound,
    ValidationError,
)
from rest_framework.test import DjangoRequestFactory

from django.core import exceptions as django_exceptions
from django.db.models import fields
from django.test import TestCase

from audoma.drf.mixins import (  # BulkUpdateModelMixin,
    ActionModelMixin,
    BulkCreateModelMixin,
    BulkUpdateModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from audoma.drf.serializers import (
    BulkListSerializer,
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

    def test_destroy_validation_error(self):
        request = self.factory.delete("/example")
        request.data = {"id": 1}

        def perform_destroy(me):
            raise django_exceptions.ValidationError("Some Validation error")

        self.view.perform_destroy = perform_destroy
        self.view.request = request
        self.view.action = "destroy"
        try:
            self.view.destroy(request)
        except Exception as e:
            self.assertEqual(type(e), ValidationError)
            self.assertEqual(str(e.detail["detail"]), "Some Validation error")


class BulkCreateModelMixinTestCase(CommonMixinTestCase):

    view_baseclasses = (BulkCreateModelMixin, GenericViewSet)

    def setUp(self):
        super().setUp()

        self.bulk_serializer_class = create_model_serializer_class(
            meta_model=self.model,
            meta_fields=["name", "age"],
            serializer_base_classes=(BulkSerializerMixin, ModelSerializer),
        )

        class ExampleBulkListSerializer(BulkListSerializer):
            def save(me):
                objs = []
                for x, d in enumerate(me.data):
                    objs.append(self.model(id=x, name=d["name"], age=d["age"]))
                me.instance = objs
                return objs

        self.bulk_serializer_class.Meta.list_serializer_class = (
            ExampleBulkListSerializer
        )

        def save(me):
            data = me.data
            me.instance = self.model(id=1, name=data["name"], age=data["age"])
            return me.instance

        self.bulk_serializer_class.save = save

        self.view.serializer_class = self.bulk_serializer_class

    def test_create_not_bulk_success(self):
        data = {"name": "John", "age": 47}
        request = self.factory.post("/example")
        request.data = data
        self.view.action = "create"
        self.view.request = request
        response = self.view.create(request, success_status=201)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, data)

    def test_create_is_bulk_success(self):
        data = [{"name": "Greg", "age": 22}, {"name": "John", "age": 47}]
        request = self.factory.post("/example")
        request.data = data
        self.view.action = "create"
        self.view.request = request
        response = self.view.create(request, success_status=201)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0], OrderedDict({"name": "Greg", "age": 22}))
        self.assertEqual(response.data[1], OrderedDict({"name": "John", "age": 47}))


class BulkUpdateMixinTestCase(CommonMixinTestCase):
    view_baseclasses = (BulkUpdateModelMixin, GenericViewSet)

    def setUp(self):
        super().setUp()

        def get_queryset():
            return [
                self.model(id=1, name="Greg", age=22),
                self.model(id=2, name="John", age=47),
            ]

        self.view.get_queryset = get_queryset
        self.bulk_serializer_class = create_model_serializer_class(
            meta_model=self.model,
            meta_fields=["id", "name", "age"],
            serializer_base_classes=(BulkSerializerMixin, ModelSerializer),
        )

        class ExampleBulkListSerializer(BulkListSerializer):
            def save(me):
                for _, d in enumerate(me.validated_data):
                    for x, i in enumerate(me.instance):
                        if i.id == d["id"]:
                            for key, value in d.items():
                                setattr(me.instance[x], key, value)

                return me.instance

        self.bulk_serializer_class.Meta.list_serializer_class = (
            ExampleBulkListSerializer
        )

        def save(me):
            data = me.data
            me.instance = self.model(id=data["id"], name=data["name"], age=data["age"])
            return me.instance

        self.bulk_serializer_class.save = save

        self.view.serializer_class = self.bulk_serializer_class

    def test_bulk_update_not_many_success(self):
        data = [{"id": 2, "name": "John", "age": 55}]
        request = self.factory.put("/example")
        request.data = data
        self.view.action = "update"
        self.view.request = request

        def filter_queryset(queryset):
            data = request.data if isinstance(request.data, list) else [request.data]
            ids = [d["id"] for d in data]
            filtered_queryset = []
            for q in queryset:
                if q.id not in ids:
                    continue
                filtered_queryset.append(q)
            return filtered_queryset

        self.view.filter_queryset = filter_queryset

        response = self.view.bulk_update(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict(data[0])])

    def test_bulk_update_many_success(self):
        data = [
            {"id": 2, "name": "John", "age": 55},
            {"id": 1, "name": "Zenon", "age": 11},
        ]
        request = self.factory.put("/example")
        request.data = data
        self.view.action = "update"
        self.view.request = request

        def filter_queryset(queryset):
            data = request.data if isinstance(request.data, list) else [request.data]
            ids = [d["id"] for d in data]
            filtered_queryset = []
            for q in queryset:
                if q.id not in ids:
                    continue
                filtered_queryset.append(q)
            return filtered_queryset

        self.view.filter_queryset = filter_queryset

        response = self.view.bulk_update(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [OrderedDict(data[1]), OrderedDict(data[0])])

    def test_partial_bulk_update_not_many_success(self):
        data = [{"id": 2, "name": "Simon"}]
        request = self.factory.put("/example")
        request.data = data
        self.view.action = "update"
        self.view.request = request

        def filter_queryset(queryset):
            data = request.data if isinstance(request.data, list) else [request.data]
            ids = [d["id"] for d in data]
            filtered_queryset = []
            for q in queryset:
                if q.id not in ids:
                    continue
                filtered_queryset.append(q)
            return filtered_queryset

        self.view.filter_queryset = filter_queryset

        response = self.view.bulk_update(request, partial=True)
        self.assertEqual(response.status_code, 200)
        data[0]["age"] = 47
        self.assertEqual(response.data, [OrderedDict(data[0])])

    def test_partial_bulk_update_many_success(self):
        data = [{"id": 2, "name": "Simon"}, {"id": 1, "name": "Caroline"}]
        request = self.factory.put("/example")
        request.data = data
        self.view.action = "update"
        self.view.request = request

        def filter_queryset(queryset):
            data = request.data if isinstance(request.data, list) else [request.data]
            ids = [d["id"] for d in data]
            filtered_queryset = []
            for q in queryset:
                if q.id not in ids:
                    continue
                filtered_queryset.append(q)
            return filtered_queryset

        self.view.filter_queryset = filter_queryset

        response = self.view.bulk_update(request, partial=True)
        self.assertEqual(response.status_code, 200)
        data[0]["age"] = 47
        data[1]["age"] = 22
        self.assertEqual(response.data, [OrderedDict(data[1]), OrderedDict(data[0])])
