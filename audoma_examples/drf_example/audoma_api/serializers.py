from datetime import date

from audoma_api.models import (
    ExampleFileModel,
    ExampleDependedModel,
    ExampleForeignKeyModel,
    ExampleModel,
)

from audoma.drf import serializers
from audoma.drf.decorators import document_and_format


class NestedExampleSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ExampleSerializer(serializers.Serializer):
    charfield_nolimits = serializers.CharField()
    charfield_min_max = serializers.CharField(min_length=5, max_length=20)
    phone_number = serializers.PhoneNumberField()
    email = serializers.EmailField()
    url = serializers.URLField()
    boolean = serializers.BooleanField()
    nullboolean = serializers.NullBooleanField()
    mac_address = serializers.MACAddressField()
    regex_mac_address = serializers.RegexField(
        regex="^([0-9A-F]{2}:){5}([0-9A-F]{2})|([0-9A-F]{2}-){5}([0-9A-F]{2})$"
    )
    slug = serializers.SlugField()
    uuid = serializers.UUIDField(format="hex")
    # file_path = serializers.FilePathField()
    ip_address = serializers.IPAddressField()
    integer = serializers.IntegerField()
    float = serializers.FloatField()
    decimal = serializers.DecimalField(max_digits=10, decimal_places=2)
    datetime = serializers.DateTimeField()
    date = serializers.DateField(example=str(date.today()))
    time = serializers.TimeField(example="12:34:56.000000")
    duration = serializers.DurationField()
    choice = serializers.ChoiceField({1: "One", 2: "Two", 3: "Three"})
    # multiple_choice = serializers.MultipleChoiceField({1: "One", 2: "Two", 3: "Three"})
    list_of_emails = serializers.ListField(child=serializers.EmailField())
    dict_of_addressess = serializers.DictField(child=serializers.EmailField())
    hstore_of_emails = serializers.HStoreField(child=serializers.EmailField())
    json = serializers.JSONField()
    readonly = serializers.ReadOnlyField()
    nested = NestedExampleSerializer()


class ExampleModelSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()

    class Meta:

        model = ExampleModel
        fields = "__all__"

    @document_and_format(serializers.PhoneNumberField)
    def get_phone_number(self):
        return self.phone_number


class ExampleFileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleFileModel


class ExampleForeignKeyModelSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        choices_link={
            "viewname": "related_model_viewset-detail",
            "destinations": {"id": "foreign_key"},
            "view_kwargs": {"pk": "id"},
        }
    )

    class Meta:
        model = ExampleForeignKeyModel
        fields = "__all__"


class ExampleDependedModelSerializer(serializers.ModelSerializer):

    foreign_key = serializers.IntegerField(
        choices_link={
            "viewname": "example_foreign_key_viewset-list",
            "sources": {"foreign_key": "id"},
        }
    )

    class Meta:
        model = ExampleDependedModel
        fields = "__all__"
