from healthcare_api import (
    models,
    serializers,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from audoma.decorators import audoma_action
from audoma.drf import mixins
from audoma.drf.viewsets import GenericViewSet


# This viewset shows how audoma works for standard drf's action and custom audoma mixins
# It also has bulk operations included
class PatientViewset(
    mixins.ListModelMixin,
    mixins.BulkCreateModelMixin,
    mixins.BulkUpdateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):

    permission_classes = [IsAuthenticated, IsAdminUser]

    serializer_class = serializers.PatientReadSerializer
    common_collect_serializer_class = serializers.PatientWriteSerializer
    get_files_serializer_class = serializers.PatientFilesDetailSerializer
    queryset = models.Patient.objects.all()
    lookup_url_kwarg = "pk"

    def filter_queryset(self, queryset):
        if self.request.method in ["PUT", "PATCH"] and isinstance(
            self.request.data, list
        ):
            ids = [d[self.lookup_url_kwarg] for d in self.request.data]
            queryset = queryset.filter(id__in=ids)
        return queryset

    @action(methods=["GET"], detail=True)
    def get_files(self, request, pk):
        files = get_object_or_404(models.PatientFiles, patient__id=pk)
        serializer = self.get_serializer(instance=files)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SpecializatioNViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = serializers.SpecializationSerializer
    queryset = models.Specialization.objects.all()


class DoctorViewset(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):

    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = models.Doctor.objects.all()
    lookup_url_kwarg = "pk"

    list_serializer_class = serializers.DoctorReadSerializer
    create_serializer_class = serializers.DoctorWriteSerializer
    update_serializer_class = serializers.DoctorWriteSerializer
    partial_update_serializer_class = serializers.DoctorWriteSerializer


class PrescriptionViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet
):
    permission_classes = [IsAuthenticated, IsAdminUser]

    list_serializer_class = serializers.PerscriptionReadSerializer
    common_result_serializer_class = serializers.PerscriptionReadSerializer
    common_collect_serializer_class = serializers.PrescrtiptionWriteSerializer
    queryset = models.Prescription.objects.all()
    lookup_url_kwarg = "pk"
    lookup_field = "id"

    @audoma_action(
        detail=True,
        methods=["post"],
        results=serializers.PerscriptionReadSerializer,
        errors=[models.Prescription.DoesNotExist],
        ignore_view_collectors=True,
    )
    def make_prescription_invalid(self, request, pk=None):
        instance = self.get_object()
        instance.is_valid = False
        instance.save()
        return instance, 200
