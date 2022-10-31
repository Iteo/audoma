from datetime import date

from audoma_api.models import (
    Car,
    CarTag,
    ExampleFileModel,
    ExampleModel,
    ExamplePerson,
    Manufacturer,
)

from audoma.choices import make_choices
from audoma.drf import serializers
from audoma.drf.decorators import document_and_format
from audoma.drf.serializers import (
    BulkListSerializer,
    BulkSerializerMixin,
)
from audoma.drf.validators import ExclusiveFieldsValidator


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

    class Meta:
        model = ExampleModel


class ExampleModelSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()

    class Meta:

        model = ExampleModel
        fields = "__all__"
        extra_kwargs = {"char_field": {"example": "lorem ipsum"}}

    @document_and_format(serializers.PhoneNumberField)
    def get_phone_number(self, obj):
        return obj.phone_number


class ExamplePersonModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamplePerson
        fields = "__all__"


class ExampleFileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleFileModel
        fields = "__all__"


class ManufacturerModelSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        list_serializer_class = BulkListSerializer
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
        fields = ["name", "body_type", "manufacturer", "engine_size", "engine_type"]


class CarTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarTag
        fields = ["name"]


class CarDetailModelSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(
        read_only=True, source="manufacturer__name"
    )

    tags = CarTagSerializer(many=True, required=False)

    class Meta:
        model = Car
        fields = [
            "id",
            "name",
            "body_type",
            "manufacturer",
            "engine_size",
            "engine_type",
            "tags",
            "manufacturer_name",
        ]

    def _handle_tags(self, tags, instance):
        names = []
        for tag in tags:
            if instance.tags.filter(name=tag["name"]).exists():
                continue
            serializer = CarTagSerializer(data=tag)
            serializer.is_valid(raise_exception=True)
            serializer.save(car_id=instance.id)
            names.append(tag["name"])

        if tags is not None:
            CarTag.objects.exclude(name__in=names).delete()

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        self._handle_tags(tags, instance)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        instance = super().create(validated_data)
        self._handle_tags(tags, instance)
        instance.refresh_from_db()
        return instance


class MutuallyExclusiveExampleSerializer(serializers.Serializer):
    class Meta:
        validators = [
            ExclusiveFieldsValidator(
                fields=[
                    "example_field",
                    "second_example_field",
                ]
            ),
            ExclusiveFieldsValidator(
                fields=[
                    "third_example_field",
                    "fourth_example_field",
                ]
            ),
        ]

    example_field = serializers.CharField(required=False)
    second_example_field = serializers.CharField(required=False)
    third_example_field = serializers.CharField(required=False)
    fourth_example_field = serializers.CharField(required=False)

    not_exclusive_field = serializers.CharField(required=False)
    second_not_exclusive_field = serializers.CharField(required=False)


class ExampleModelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleModel
        fields = "__all__"

    def update(self):
        for key, item in self.validated_data.items():
            setattr(self.instance, key, item)
        return self.instance

    def create(self):
        return ExampleModel(
            char_field=self.validated_data["char_field"],
            phone_number=self.validated_data["phone_number"],
            email=self.validated_data["email"],
            url=self.validated_data["url"],
            boolean=self.validated_data["boolean"],
            nullboolean=self.validated_data["nullboolean"],
            mac_adress=self.validated_data["mac_adress"],
            slug=self.validated_data["slug"],
            uuid=self.validated_data["uuid"],
            ip_address=self.validated_data["ip_address"],
            integer=self.validated_data["integer"],
            _float=self.validated_data["_float"],
            decimal=self.validated_data["decimal"],
            datetime=self.validated_data["datetime"],
            date=self.validated_data["date"],
            time=self.validated_data["time"],
            duration=self.validated_data["duration"],
            choices=self.validated_data["choices"],
            json=self.validated_data["json"],
        )

    def save(self, **kwargs):
        if self.instance:
            return self.update()
        return self.create()


class ExampleOneFieldSerializer(serializers.Serializer):

    RATES = make_choices("RATE", ((0, "LIKE", "Like"), (1, "DISLIKIE", "Dislike")))

    rate = serializers.ChoiceField(choices=RATES.get_choices())

    def save(self, **kwargs):
        return self.data
