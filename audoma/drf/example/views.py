from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from audoma.drf import mixins
from audoma.drf import viewsets
from audoma.drf.example.permissions import AlternatePermission1
from audoma.drf.example.permissions import AlternatePermission2
from audoma.drf.example.permissions import DetailPermission
from audoma.drf.example.permissions import ViewAndDetailPermission
from audoma.drf.example.permissions import ViewPermission
from audoma.drf.example.serializers import ExampleSerializer


class ExampleViewSet(
        mixins.ActionModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [
        IsAuthenticated, ViewAndDetailPermission, DetailPermission, ViewPermission,
        AlternatePermission1 | AlternatePermission2
    ]
    # permission_classes = [
    #     IsAuthenticated, ViewAndDetailPermission, DetailPermission, ViewPermission,
    #     AlternatePermission1 | AlternatePermission2
    # ]

    serializer_class = ExampleSerializer
    queryset = {}

    @action(detail=True, methods=['post'])
    def detail_action(self, request, pk=None):
        return Response({})  # wrong

    @action(detail=False, methods=['post'])
    def non_detail_action(self, request):
        return Response({})  # wrong
