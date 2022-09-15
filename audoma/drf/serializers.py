from typing import (
    Any,
    List,
    Tuple,
    Type,
    Union,
)
from uuid import UUID

from rest_framework import serializers
from rest_framework.serializers import *  # noqa: F403, F401

from django.db import models
from django.db.models import QuerySet

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
    def __init__(self, result: Any, many: bool = False) -> Any:
        if many:
            self.results = result
        else:
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

        class ManyResultSerializer(serializers.Serializer):
            results = SerializerClass(many=True)

            def __init__(self, instance: Any = None, **kwargs) -> None:
                instance = Result(instance, many=True)
                super().__init__(instance=instance, **kwargs)

        class ResultSerializer(serializers.Serializer):
            result = SerializerClass()

            def __new__(cls, *args, **kwargs) -> Serializer:
                _many = kwargs.pop("many", False)
                if _many:
                    instance = ManyResultSerializer(*args, **kwargs)
                else:
                    instance = super().__new__(cls, *args, **kwargs)
                return instance

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
    def get_result_serializer_class(
        cls,
    ) -> Type[serializers.BaseSerializer]:
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

    def to_internal_value(self, data: str) -> dict:
        try:
            return self.choices_inverted_dict[data.title()]
        except KeyError:
            raise serializers.ValidationError('"%s" is not valid choice.' % data)


class ListSerializer(ResultSerializerClassMixin, serializers.ListSerializer):
    pass


class BulkSerializerMixin:
    @property
    def id_attr(self):
        return getattr(self.Meta, "id_field", "id")

    @property
    def id_lookup_field(self):
        return self.fields.get(self.id_attr).source or self.id_attr

    def validate(self, data):
        pk_field_name = getattr(self.Meta, "id_field_db_field_name", "id")

        if self.instance is not None and isinstance(self.instance, QuerySet):
            data_pk = data.get(self.id_attr)
            existing_pks = [
                str(x) if isinstance(x, UUID) else x
                for x in self.instance.values_list(pk_field_name, flat=True)
            ]
            if data_pk not in existing_pks:
                raise serializers.ValidationError(
                    {self.id_attr: "Record with given key does not exist."}
                )
        return super().validate(data)

    def to_internal_value(self, data: dict) -> dict:
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

    @property
    def id_attr(self):
        return getattr(self.child.Meta, "id_field", "id")

    @property
    def id_lookup_field(self):
        return self.child.fields.get(self.id_attr).source or self.id_attr

    def data_by_id(self, data):
        return {i.pop(self.id_attr): i for i in data}

    def objects_to_update(self, queryset, data):
        return queryset.filter(
            **{
                "{}__in".format(self.id_lookup_field): data.keys(),
            }
        )

    def update(self, queryset: QuerySet, all_validated_data: List[dict]) -> List[Any]:
        updated_objects = []
        all_validated_data_by_id = self.data_by_id(all_validated_data)

        objects_to_update = self.objects_to_update(queryset, all_validated_data_by_id)

        for obj in objects_to_update:
            obj_id = getattr(obj, self.id_attr)
            if isinstance(obj_id, UUID):
                obj_id = str(obj_id)
            obj_validated_data = all_validated_data_by_id.get(obj_id)
            # use model serializer to actually update the model
            # in case that method is overwritten
            updated_objects.append(self.child.update(obj, obj_validated_data))

        return updated_objects


class DefaultMessageSerializer(Serializer):

    message = CharField(max_length=255)
