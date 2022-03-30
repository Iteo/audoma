from datetime import date

from audoma_api.models import (
    ExampleModel,
    ExamplePerson,
)

from audoma.drf import serializers
from audoma.drf.decorators import document_and_format


class NestedExampleSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ExampleSerializer(serializers.Serializer):
    charfield_nolimits = serializers.CharField()
    charfield_min_max = serializers.CharField(min_length=5, max_length=20)
    phone_number = serializers.PhoneNumberField()
    phone_number_example = serializers.PhoneNumberField(example="+48 123 456 789")
    phone_number_region_japan = serializers.PhoneNumberField(region="JP")
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
    integer = serializers.IntegerField(min_value=25, max_value=30)
    float = serializers.FloatField(min_value=1.0, max_value=4.0)
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
        extra_kwargs = {"char_field": {"example": "lorem ipsum"}}

    @document_and_format(serializers.PhoneNumberField)
    def get_phone_number(self):
        return self.phone_number


class ExamplePersonModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamplePerson
        fields = "__all__"
