from typing import (
    Any,
    Dict,
    Iterable,
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
from rest_framework.serializers import BaseSerializer
from rest_framework.test import APIRequestFactory
from rest_framework.viewsets import ViewSet

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
        GenericViewSet,
        ActionModelMixin,
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


def create_serializer_class(
    fields_config: Dict[str, Field],
    serializer_base_classes: Iterable[Type],
    validators: Iterable[Any] = None,
) -> Type[BaseSerializer]:
    validators = validators or []

    class ExampleSerializer(*serializer_base_classes):
        ...

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


# TODO consider rewrite it using existing methods
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
        GenericViewSet,
        ActionModelMixin,
    )
    view_properties = view_properties or {}
    action_args = action_args or ()
    action_kwargs = action_kwargs or {}

    class ExampleView(*view_baseclasses):
        @action(name=action_name, *action_args, **action_kwargs)
        def fun(self, *args, **kwargs):
            ...

    for key, prop in view_properties.items():
        setattr(ExampleView, key, prop)

    ExampleView.__doc__ = docstring

    serializer_name = f"{action_name}_serializer_class"
    ExampleView.fun.__name__ = action_name

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
        GenericViewSet,
        ActionModelMixin,
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
