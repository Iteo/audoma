from healthcare_api import models as api_models

from audoma.drf import serializers


class ContactDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.ContactData
        fields = ["phone_number", "mobile", "country", "city"]


class PersonBaseSerializer(serializers.ModelSerializer):
    contact_data = ContactDataSerializer()

    def update(self, instance, validated_data):
        contact_data = validated_data.pop("contact_data", {})
        if not instance.contact_data:
            instance.contact_data = api_models.ContactData.objects.create(
                **contact_data
            )
        else:
            api_models.ContactData.objects.filter(pk=instance.contact_data.pk).update(
                **contact_data
            )
        instance = super().update(instance, validated_data)
        instance.contact_data.refresh_from_db()
        return instance

    def create(self, validated_data):
        contact_info = validated_data.pop("contact_data")
        validated_data["contact_data"] = api_models.ContactData.objects.create(
            **contact_info
        )
        return self.Meta.model.objects.create(**validated_data)


class PatientReadSerializer(PersonBaseSerializer):
    class Meta:
        model = api_models.Patient
        fields = ["name", "surname", "contact_data", "weight", "height"]


class PatientWriteSerializer(serializers.BulkSerializerMixin, PersonBaseSerializer):

    pk = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = api_models.Patient
        fields = ["pk", "name", "surname", "contact_data", "weight", "height"]
        list_serializer_class = serializers.BulkListSerializer
        id_field = "pk"


class PatientFilesEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.FileEntry
        fields = ["created_at", "modifed_at", "title", "content"]


class PatientFilesDetailSerializer(serializers.ModelSerializer):

    patient = PatientReadSerializer()
    entries = PatientFilesEntrySerializer(many=True)

    class Meta:
        model = api_models.PatientFiles
        fields = ["patient", "entries"]


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Specialization
        fields = ["id", "name"]


class DoctorReadSerializer(PersonBaseSerializer):

    specialization = SpecializationSerializer(many=True)

    class Meta:
        model = api_models.Doctor
        fields = ["name", "surname", "contact_data", "specialization"]


class DoctorWriteSerializer(PersonBaseSerializer):

    choices_options_links = {
        "specialization": {
            "viewname": "specialization-list",
            "value_field": "id",
            "display_field": "name",
        }
    }

    specialization = serializers.SerializerMethodField(
        field=serializers.ListField(child=serializers.IntegerField()), writable=True
    )

    def get_specialization(self, doctor):
        return doctor.specialization.values_list("id", flat=True)

    def validate(self, attrs):
        self.specialization_pks = attrs.pop("specialization", [])
        return attrs

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        for s in api_models.Specialization.objects.filter(
            pk__in=self.specialization_pks
        ):
            instance.specialization.add(s)
        instance.save()
        return instance

    class Meta:
        model = api_models.Doctor
        fields = ["name", "surname", "contact_data", "specialization", "salary"]


class PerscriptionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Prescription
        fields = [
            "issued_by",
            "issued_for",
            "drugs",
            "usable_in",
            "issued_in",
            "is_valid",
        ]


class PrescrtiptionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Prescription
        fields = ["issued_by", "issued_for", "drugs", "usable_in", "issued_in"]
