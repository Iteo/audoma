from typing import (
    Any,
    Tuple,
    Type,
    Union,
)

from rest_framework import serializers
from rest_framework.serializers import *  # noqa: F403, F401

from django.db import models

from audoma import settings
from audoma.django.db import models as audoma_models


try:
    from django.db.models import JSONField as ModelJSONField
except ImportError:
    try:
        from jsonfield import JSONField as ModelJSONField
    except ImportError as err:
        raise ImportError(
            "You are using old version of Django that doesn't support JSONField. Please install django-jsonfield"
        ) from err


from audoma.drf.fields import (  # NOQA # isort:skip
    BooleanField,
    CharField,
    ChoiceField,
    DateField,
    DateTimeField,
    DecimalField,
    DictField,
    DurationField,
    EmailField,
    Field,
    FileField,
    FilePathField,
    FloatField,
    HiddenField,
    HStoreField,
    IPAddressField,
    ImageField,
    IntegerField,
    JSONField,
    ListField,
    ModelField,
    MultipleChoiceField,
    NullBooleanField,
    ReadOnlyField,
    RegexField,
    SerializerMethodField,
    SlugField,
    TimeField,
    URLField,
    UUIDField,
    MACAddressField,
    PhoneNumberField,
    MoneyField,
)


embeded_serializer_classes = {}


class Result:
    def __init__(self, result: Any) -> None:
        self.result = result


def result_serializer_class(
    SerializerClass: Type[serializers.BaseSerializer],
) -> Type[serializers.BaseSerializer]:
    """
    Helper function which wraps the serializer result if necessary.

    Args:
        * SerializerClass - serializer class which result should be wrapped

    Returns: ResultSerializer class
    """
    if SerializerClass not in embeded_serializer_classes:
        class_name = SerializerClass.__name__
        if class_name.endswith("Serializer"):
            class_name = class_name[:-10] + "ResultSerializer"
        else:
            class_name += "Result"

        class ResultSerializer(serializers.Serializer):
            result = SerializerClass()

            def __init__(self, instance: Any = None, **kwargs) -> None:
                instance = Result(instance)
                super().__init__(instance=instance, **kwargs)

        ResultSerializer.__name__ = class_name
        embeded_serializer_classes[SerializerClass] = ResultSerializer
    return embeded_serializer_classes[SerializerClass]


class ResultSerializerClassMixin:
    """
    Allows to define wrap for serializer result.
    """

    _wrap_result_serializer = settings.WRAP_RESULT_SERIALIZER

    @classmethod
    def get_result_serializer_class(cls) -> Type[serializers.BaseSerializer]:
        if cls._wrap_result_serializer:
            return result_serializer_class(cls)
        return cls


class ModelSerializer(ResultSerializerClassMixin, serializers.ModelSerializer):
    """
    Extends default ModelSerializer,
    modifies serializer_field_mapping (replaces some fields with audoma fields).
    Adds support for generating audoma example for field.
    """

    serializer_field_mapping = {
        models.AutoField: IntegerField,
        models.BigIntegerField: IntegerField,
        models.BooleanField: BooleanField,
        models.CharField: CharField,
        models.CommaSeparatedIntegerField: CharField,
        models.DateField: DateField,
        models.DateTimeField: DateTimeField,
        models.DecimalField: DecimalField,
        models.DurationField: DurationField,
        models.EmailField: EmailField,
        models.Field: ModelField,
        models.FileField: FileField,
        models.FloatField: FloatField,
        models.ImageField: ImageField,
        models.IntegerField: IntegerField,
        models.NullBooleanField: NullBooleanField,
        models.PositiveIntegerField: IntegerField,
        models.PositiveSmallIntegerField: IntegerField,
        models.SlugField: SlugField,
        models.SmallIntegerField: IntegerField,
        models.TextField: CharField,
        models.TimeField: TimeField,
        models.URLField: URLField,
        models.GenericIPAddressField: IPAddressField,
        models.FilePathField: FilePathField,
        models.UUIDField: UUIDField,
        audoma_models.PhoneNumberField: PhoneNumberField,
        audoma_models.MACAddressField: MACAddressField,
        audoma_models.MoneyField: MoneyField,
        audoma_models.CurrencyField: CharField,
        ModelJSONField: JSONField,
    }

    serializer_choice_field = ChoiceField

    def build_standard_field(
        self, field_name, model_field
    ) -> Tuple[Union[Type[Field], dict]]:
        """
        Adds support for mapping example from model fields to model serializer fields.
        """
        field_class, field_kwargs = super().build_standard_field(
            field_name, model_field
        )
        if hasattr(model_field, "example") and model_field.example:
            field_kwargs["example"] = model_field.example
        return field_class, field_kwargs


class Serializer(ResultSerializerClassMixin, serializers.Serializer):
    pass


class DisplayNameWritableField(serializers.ChoiceField):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.choices_inverted_dict = dict((y, x) for x, y in list(self.choices.items()))
        self.original_choices = self.choices
        self.choices = dict((y, y) for x, y in list(self.original_choices.items()))

    def to_representation(self, value: Any) -> Any:
        # serializer_field.parentu
        return self.original_choices.get(value, value)

    def to_internal_value(self, data: str) -> Any:
        try:
            return self.choices_inverted_dict[data.title()]
        except KeyError:
            raise serializers.ValidationError('"%s" is not valid choice.' % data)
