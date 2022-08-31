import random
import string
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Tuple,
    Type,
    Union,
)

from rest_framework.decorators import action
from rest_framework.fields import (
    Field,
    SerializerMethodField,
)
from rest_framework.request import Request
from rest_framework.serializers import (
    BaseSerializer,
    ModelSerializer,
)
from rest_framework.test import APIRequestFactory
from rest_framework.viewsets import ViewSet

from django.db.models import Model

from audoma.decorators import audoma_action
from audoma.drf.mixins import (
    ActionModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from audoma.drf.viewsets import GenericViewSet


_factory = APIRequestFactory()


def create_basic_view_class(
    docstring: str = "Test View Doc",
    view_baseclasses: Iterable[Type] = None,
    view_properties: Dict[str, Any] = None,
) -> Type[ViewSet]:
    view_baseclasses = view_baseclasses or (
        ListModelMixin,
        RetrieveModelMixin,
        ActionModelMixin,
        GenericViewSet,
    )
    view_properties = view_properties or {}

    class ExampleView(*view_baseclasses):
        ...

    for key, prop in view_properties.items():
        setattr(ExampleView, key, prop)

    ExampleView.__doc__ = docstring
    return ExampleView


def create_basic_view(
    docstring: str = "Test View Doc",
    view_baseclasses: Iterable[Type] = None,
    view_properties: Dict[str, Any] = None,
) -> ViewSet:
    return create_basic_view_class(docstring, view_baseclasses, view_properties)()


def _get_random_name(k: int = 10):
    word = "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=k))
    return word


def create_model_class(
    fields_config: Dict[str, Field],
    model_base_classes: Iterable[Type] = None,
):
    model_base_classes = model_base_classes or (Model,)

    class Meta:
        app_label = "audoma_api"

    model_props = {"Meta": Meta, "__module__": "Example"}
    model_props.update(fields_config)
    model_name = _get_random_name()

    model = type(model_name, model_base_classes, model_props)

    return model


def create_serializer_class(
    fields_config: Dict[str, Field],
    serializer_base_classes: Iterable[Type],
    validators: Iterable[Any] = None,
) -> Type[BaseSerializer]:
    validators = validators or []

    class ExampleSerializer(*serializer_base_classes):
        # Mock serializer save to prevent
        # db connection for mocked serializer
        def save(self, **kwargs):
            if isinstance(self, ModelSerializer):
                instance = self.Meta.model()
                for item, value in self.validated_data.items():
                    setattr(instance, item, value)
                self.instance = instance
                return instance
            return self.validated_data

    for field_name, field in fields_config.items():
        setattr(ExampleSerializer, field_name, field)
        ExampleSerializer._declared_fields[field_name] = field
        if isinstance(field, SerializerMethodField):
            name = field.source or f"get_{field_name}"
            setattr(ExampleSerializer, name, lambda x: None)

    ExampleSerializer.validators = validators

    return ExampleSerializer


def create_serializer(
    fields_config: Dict[str, Field],
    serializer_base_classes: Iterable[Type],
    validators: Iterable[Any] = None,
) -> BaseSerializer:
    return create_serializer_class(fields_config, serializer_base_classes, validators)()


def create_model_serializer_class(
    meta_model: Model,
    serializer_base_classes: Iterable[Type] = (ModelSerializer,),
    meta_fields: Union[str, List[str]] = "__all__",
    fields_config: Dict[str, Field] = {},
    validators: Iterable[Any] = None,
):
    serializer = create_serializer_class(
        fields_config, serializer_base_classes, validators
    )

    class Meta:
        model = meta_model
        fields = meta_fields

    setattr(serializer, "Meta", Meta)
    return serializer


def create_view_with_custom_action(
    docstring: str = "Test View Doc",
    view_baseclasses: Iterable[Type] = None,
    view_properties: Dict[str, Any] = None,
    action_name: str = "custom_action",
    action_serializer_class: BaseSerializer = None,
    action_args: Iterable[Any] = None,
    action_kwargs: Dict[str, Any] = None,
):
    view_baseclasses = view_baseclasses or (
        ListModelMixin,
        RetrieveModelMixin,
        ActionModelMixin,
        GenericViewSet,
    )
    view_properties = view_properties or {}
    action_args = action_args or ()
    action_kwargs = action_kwargs or {}

    class ExampleView(*view_baseclasses):
        permissions_classes = []

        @action(name=action_name, *action_args, **action_kwargs)
        def fun(self, *args, **kwargs):
            ...

    for key, prop in view_properties.items():
        setattr(ExampleView, key, prop)

    ExampleView.__doc__ = docstring

    serializer_name = f"{action_name}_serializer_class"
    ExampleView.fun.__name__ = action_name
    ExampleView.action_name = ExampleView.fun

    if action_serializer_class is not None:
        setattr(ExampleView, serializer_name, action_serializer_class)
    return ExampleView()


def create_view_with_custom_audoma_action(
    docstring: str = "Test View Doc",
    view_baseclasses: Iterable[Type] = None,
    view_properties: Dict[str, Any] = None,
    request: Request = None,
    action_name: str = "custom_action",
    action_serializer_class: BaseSerializer = None,
    action_args: Iterable[Any] = None,
    action_kwargs: Dict[str, Any] = None,
    returnables: Tuple[int, Any] = None,
    raiseable: Union[Exception, Type[Exception]] = None,
    raise_exception: bool = False,
):
    view_baseclasses = view_baseclasses or (
        ListModelMixin,
        RetrieveModelMixin,
        ActionModelMixin,
        GenericViewSet,
    )
    view_properties = view_properties or {}
    action_args = action_args or ()
    action_kwargs = action_kwargs or {}
    returnables = returnables or ({}, 200)
    raiseable = raiseable or Exception
    Request or _factory.get("/test-request/")

    class ExampleView(*view_baseclasses):
        @audoma_action(name=action_name, *action_args, **action_kwargs)
        def fun(self, request, *args, **kwargs):
            if raise_exception:
                raise raiseable
            return returnables

    for key, prop in view_properties.items():
        setattr(ExampleView, key, prop)

    ExampleView.__doc__ = docstring

    serializer_name = f"{action_name}_serializer_class"
    ExampleView.fun.__name__ = action_name
    setattr(ExampleView, action_name, ExampleView.fun)
    if action_serializer_class is not None:
        setattr(ExampleView, serializer_name, action_serializer_class)
    return ExampleView()
