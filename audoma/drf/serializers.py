import inspect

import jsonfield
from rest_framework import serializers
from rest_framework.serializers import *  # noqa: F403, F401

from django.db import models

from audoma import (
    django_modelfields,
    settings,
)


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
)


embeded_serializer_classes = {}


class Result:
    def __init__(self, result, many=False):
        if many:
            self.results = result
        else:
            self.result = result


def result_serializer_class(SerializerClass, many=False):
    if SerializerClass not in embeded_serializer_classes:
        class_name = SerializerClass.__name__
        if class_name.endswith("Serializer"):
            class_name = class_name[:-10] + "ResultSerializer"
        else:
            class_name += "Result"

        class ManyResultSerializer(serializers.Serializer):
            results = SerializerClass(many=True)

            def __init__(self, instance=None, **kwargs):
                instance = Result(instance, many=True)
                super().__init__(instance=instance, **kwargs)

        class ResultSerializer(serializers.Serializer):
            result = SerializerClass()

            def __new__(cls, *args, **kwargs):
                _many = kwargs.pop("many", False)

                if _many:
                    instance = ManyResultSerializer(*args, **kwargs)
                else:
                    instance = super().__new__(cls, *args, **kwargs)
                return instance

            def __init__(self, instance=None, **kwargs):
                instance = Result(instance, many=False)
                super().__init__(instance=instance, **kwargs)

        ResultSerializer.__name__ = class_name
        embeded_serializer_classes[SerializerClass] = ResultSerializer
    return embeded_serializer_classes[SerializerClass]


class ResultSerializerClassMixin:
    _wrap_result_serializer = settings.WRAP_RESULT_SERIALIZER

    @classmethod
    def get_result_serializer_class(cls, many=False):
        if cls._wrap_result_serializer:
            return result_serializer_class(cls, many=many)
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
    }


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


class ListSerializer(ResultSerializerClassMixin, serializers.ListSerializer):
    pass


class BulkSerializerMixin:
    def to_internal_value(self, data):
        ret = super().to_internal_value(data)

        id_attr = getattr(self.Meta, "id_field", "id")
        request_method = getattr(
            getattr(self.context.get("view"), "request"), "method", ""
        )

        # add id_field field back to validated data
        # since super by default strips out read-only fields
        # hence id will no longer be present in validated_data

        if all(
            (
                isinstance(self.root, BulkListSerializer),
                id_attr,
                request_method in ("PUT", "PATCH"),
            )
        ):
            id_field = self.fields[id_attr]
            id_value = id_field.get_value(data)

            ret[id_attr] = id_value

        return ret


class BulkListSerializer(ListSerializer):
    id_field = "id"

    def get_unique_fields(self):
        return []

    def validate(self, attrs):
        ret = super().validate(attrs)
        return ret

    def update(self, queryset, all_validated_data):
        from uuid import UUID

        id_attr = getattr(self.child.Meta, "id_field", "id")
        all_validated_data_by_id = {i.pop(id_attr): i for i in all_validated_data}

        if not all(
            (
                bool(i) and not inspect.isclass(i)
                for i in all_validated_data_by_id.keys()
            )
        ):
            raise ValidationError("")

        # since this method is given a queryset which can have many
        # model instances, first find all objects to update
        # and only then update the models
        id_lookup_field = self.child.fields.get(id_attr).source or id_attr
        objects_to_update = queryset.filter(
            **{
                "{}__in".format(id_lookup_field): all_validated_data_by_id.keys(),
            }
        )

        if len(all_validated_data_by_id) != objects_to_update.count():
            raise ValidationError("Could not find all objects to update.")

        updated_objects = []

        for obj in objects_to_update:
            obj_id = getattr(obj, id_attr)
            if isinstance(obj_id, UUID):
                obj_id = str(obj_id)
            obj_validated_data = all_validated_data_by_id.get(obj_id)
            # use model serializer to actually update the model
            # in case that method is overwritten
            updated_objects.append(self.child.update(obj, obj_validated_data))

        return updated_objects
