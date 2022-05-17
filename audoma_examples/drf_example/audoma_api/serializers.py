from datetime import date

from audoma_api.models import (
    Account,
    Auction,
    Car,
    ExampleSimpleModel,
    ExampleTagModel,
    Manufacturer,
)

from audoma.choices import make_choices
from audoma.drf import serializers
from audoma.drf.decorators import document_and_format


class NestedExampleSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ExampleSerializer(serializers.Serializer):
    charfield_nolimits = serializers.CharField()
    charfield_min_max = serializers.CharField(min_length=10, max_length=20)
    phone_number = serializers.PhoneNumberField()
    phone_number_example = serializers.PhoneNumberField(example="+48 123 456 789")
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
    money = serializers.MoneyField(max_digits=10, decimal_places=2)
    choice = serializers.ChoiceField({1: "One", 2: "Two", 3: "Three"})
    # multiple_choice = serializers.MultipleChoiceField({1: "One", 2: "Two", 3: "Three"})
    list_of_emails = serializers.ListField(child=serializers.EmailField())
    dict_of_addressess = serializers.DictField(child=serializers.EmailField())
    hstore_of_emails = serializers.HStoreField(child=serializers.EmailField())
    json = serializers.JSONField()
    readonly = serializers.ReadOnlyField()
    nested = NestedExampleSerializer()


class AccountModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class AuctionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = "__all__"


class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"

    def update(self):
        for key, item in self.validated_data.items():
            setattr(self.instance, key, item)
        return self.instance

    def create(self):
        return Account(
            username=self.validated_data["username"],
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
            phone_number=self.validated_data["phone_number"],
            nationality=self.validated_data["nationality"],
            city=self.validated_data["city"],
            email=self.validated_data["email"],
            bio=self.validated_data["bio"],
            is_active=self.validated_data["is_active"],
            mac_adress=self.validated_data["mac_adress"],
            ip_address=self.validated_data["ip_address"],
            age=self.validated_data["age"],
            _float=self.validated_data["_float"],
            decimal=self.validated_data["decimal"],
            duration=self.validated_data["duration"],
            account_type=self.validated_data["account_type"],
            account_balance=self.validated_data["account_balance"],
        )

    def save(self, **kwargs):
        if self.instance:
            return self.update()
        return self.create()


class RateSerializer(serializers.Serializer):

    RATES = make_choices("RATE", ((0, "LIKE", "Like"), (1, "DISLIKE", "Dislike")))

    rate = serializers.ChoiceField(choices=RATES.get_api_choices())

    def save(self, **kwargs):
        return self.validated_data


class ManufacturerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = "__all__"


class CarModelSerializer(serializers.ModelSerializer):

    choices_options_links = {
        "manufacturer": {
            "viewname": "manufacturer_viewset-list",
            "value_field": "id",
            "display_field": "name",
        }
    }

    manufacturer = serializers.IntegerField()

    class Meta:
        model = Car
        fields = "__all__"


class ExampleSimpleModelSerializer(
    serializers.ModelSerializer, serializers.BulkSerializerMixin
):
    class Meta:
        model = ExampleSimpleModel
        fields = "__all__"
        list_serializer_class = serializers.BulkListSerializer
