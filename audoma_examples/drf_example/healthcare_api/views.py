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

# from audoma.decorators import audoma_action
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

    @action(methods=["GET"], detail=True)
    def get_files(self, request, id):
        files = models.PatientFiles.objects.get(patient__id=id)
        serializer = self.get_serializer(instance=files)
        return Response(serializer.data, status=status.HTTP_200_OK)
