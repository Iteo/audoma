import jsonfield
from rest_framework import serializers
from rest_framework.serializers import *  # noqa: F403, F401

from django.db import models

from audoma import (
    django_modelfields,
    settings,
)
from audoma.django.db.models import MoneyField as ModelMoneyField


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
    def __init__(self, result):
        self.result = result


def result_serializer_class(SerializerClass):
    if SerializerClass not in embeded_serializer_classes:
        class_name = SerializerClass.__name__
        if class_name.endswith("Serializer"):
            class_name = class_name[:-10] + "ResultSerializer"
        else:
            class_name += "Result"

        class ResultSerializer(serializers.Serializer):
            result = SerializerClass()

            def __init__(self, instance=None, **kwargs):
                instance = Result(instance)
                super().__init__(instance=instance, **kwargs)

        ResultSerializer.__name__ = class_name
        embeded_serializer_classes[SerializerClass] = ResultSerializer
    return embeded_serializer_classes[SerializerClass]


class ResultSerializerClassMixin:
    _wrap_result_serializer = settings.WRAP_RESULT_SERIALIZER

    @classmethod
    def get_result_serializer_class(cls):
        if cls._wrap_result_serializer:
            return result_serializer_class(cls)
        return cls


class ModelSerializer(ResultSerializerClassMixin, serializers.ModelSerializer):
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
        django_modelfields.PhoneNumberField: PhoneNumberField,
        django_modelfields.MACAddressField: MACAddressField,
        jsonfield.JSONField: JSONField,
        ModelMoneyField: MoneyField,
    }

    serializer_choice_field = ChoiceField

    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super().build_standard_field(
            field_name, model_field
        )
        if hasattr(model_field, "example") and model_field.example:
            field_kwargs["example"] = model_field.example
        return field_class, field_kwargs


class Serializer(ResultSerializerClassMixin, serializers.Serializer):
    pass


class DisplayNameWritableField(serializers.ChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices_inverted_dict = dict((y, x) for x, y in list(self.choices.items()))
        self.original_choices = self.choices
        self.choices = dict((y, y) for x, y in list(self.original_choices.items()))

    def to_representation(self, value):
        # serializer_field.parentu
        return self.original_choices.get(value, value)

    def to_internal_value(self, data):
        try:
            return self.choices_inverted_dict[data.title()]
        except KeyError:
            raise serializers.ValidationError('"%s" is not valid choice.' % data)
