from healthcare_api import models as api_models

from audoma.drf import serializers


class ContactDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.ContactData
        fields = ["phone_number", "mobile", "country", "city"]


class PersonBaseSerializer(serializers.ModelSerializer):
    contact_data = ContactDataSerializer()


class PatientReadSerializer(PersonBaseSerializer):
    class Meta:
        model = api_models.Patient
        fields = ["name", "surname", "contact_data", "weight", "height"]


class PatientWriteSerializer(serializers.BulkSerializerMixin, PersonBaseSerializer):
    class Meta:
        model = api_models.Patient
        fields = ["name", "surname", "contact_data", "weight", "height"]
        list_serializer = serializers.BulkListSerializer

    def update(self, validated_data):
        ...

    def create(self, validated_data):
        contact_info = validated_data.pop("contact_data")
        validated_data["contact_data"] = api_models.ContactData.objects.create(
            **contact_info
        )
        return api_models.Patient.objects.create(**validated_data)


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
        fields = ["name"]


class DoctorReadSerializer(PersonBaseSerializer):

    specialization = SpecializationSerializer(many=True)

    class Meta:
        model = api_models.Doctor
        fields = ["name", "surname", "contact_data", "specialization"]


# TODO - finish this
class DoctorWriteSerializer(PersonBaseSerializer):

    specialization = serializers.CharField()

    class Meta:
        model = api_models.Doctor
        fields = ["name", "surname", "contact_data", "specialization"]
