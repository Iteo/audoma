# import inspect

import random
import uuid

from django.utils.functional import lazy
from rest_framework import serializers

embeded_serializer_classes = {}


class Result:
    def __init__(self, result):
        self.result = result


def result_serializer_class(SerializerClass):
    if SerializerClass not in embeded_serializer_classes:
        class_name = SerializerClass.__name__
        if class_name.endswith('Serializer'):
            class_name = class_name[:-10] + 'ResultSerializer'
        else:
            class_name += 'Result'

        class ResultSerializer(serializers.Serializer):
            result = SerializerClass()

            def __init__(self, instance=None, **kwargs):
                instance = Result(instance)
                super().__init__(instance=instance, **kwargs)

        ResultSerializer.__name__ = class_name
        embeded_serializer_classes[SerializerClass] = ResultSerializer
    return embeded_serializer_classes[SerializerClass]


class ResultSerializerClassMixin:

    @classmethod
    def get_result_serializer_class(cls):
        return result_serializer_class(cls)


class ModelSerializer(ResultSerializerClassMixin, serializers.ModelSerializer):
    pass


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


class DecimalField(serializers.DecimalField):
    class Meta:
        swagger_schema_fields = {
            "example": lazy(lambda: "%.2f" % (random.random() * random.randint(1, 1000)), str)()
        }


class UUIDField(serializers.UUIDField):
    class Meta:
        swagger_schema_fields = {
            "example": lazy(lambda: str(uuid.uuid4()), str)()
        }


class IntegerField(serializers.IntegerField):
    class Meta:
        swagger_schema_fields = {
            "example": lazy(lambda: random.randint(1, 1000), int)()
        }


class FloatField(serializers.FloatField):
    class Meta:
        swagger_schema_fields = {
            "example": lazy(lambda: (random.random() * random.randint(1, 1000)), float)()
        }
