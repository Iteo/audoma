from rest_framework import serializers


class NestedExampleSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ExampleSerializer(serializers.Serializer):
    charfield_nolimits = serializers.CharField()
    charfield_min_max = serializers.CharField(min_length=5, max_length=20)
    email = serializers.EmailField()
    url = serializers.URLField()
    boolean = serializers.BooleanField()
    nullboolean = serializers.NullBooleanField()
    regex_mac_address = serializers.RegexField(regex="^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$")
    slug = serializers.SlugField()
    uuid = serializers.UUIDField()
    # file_path = serializers.FilePathField()
    ip_address = serializers.IPAddressField()
    integer = serializers.IntegerField()
    float = serializers.FloatField()
    decimal = serializers.DecimalField(max_digits=10, decimal_places=2)
    datetime = serializers.DateTimeField()
    date = serializers.DateField()
    time = serializers.TimeField()
    duration = serializers.DurationField()
    choice = serializers.ChoiceField({1: "One", 2: "Two", 3: "Three"})
    multiple_choice = serializers.MultipleChoiceField({1: "One", 2: "Two", 3: "Three"})
    list_of_emails = serializers.ListField(child=serializers.EmailField())
    dict_of_addressess = serializers.DictField(child=serializers.EmailField())
    hstore_of_emails = serializers.HStoreField(child=serializers.EmailField())
    json = serializers.JSONField()
    readonly = serializers.ReadOnlyField
    nested = NestedExampleSerializer()

# TODO: example file uploads
