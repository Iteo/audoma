from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from v2_api import mixins as v2_mixins
from v2_api import viewsets as v2_viewsets
from v2_api.example.permissions import AlternatePermission1
from v2_api.example.permissions import AlternatePermission2
from v2_api.example.permissions import DetailPermission
from v2_api.example.permissions import ViewAndDetailPermission
from v2_api.example.permissions import ViewPermission
from v2_api.example.serializers import ExampleSerializer


class ExampleViewSet(
        v2_mixins.ActionModelMixin, v2_mixins.CreateModelMixin, v2_mixins.RetrieveModelMixin,
        v2_mixins.DestroyModelMixin, v2_mixins.ListModelMixin, v2_viewsets.GenericViewSet):
    permission_classes = [
        IsAuthenticated, ViewAndDetailPermission, DetailPermission, ViewPermission,
        AlternatePermission1 | AlternatePermission2
    ]
    # permission_classes = [
    #     IsAuthenticated, ViewAndDetailPermission, DetailPermission, ViewPermission,
    #     AlternatePermission1 | AlternatePermission2
    # ]

    serializer_class = ExampleSerializer

    @action(detail=True, methods=['post'])
    def detail_action(self, request, pk=None):
        return Response({})  # wrong

    @action(detail=False, methods=['post'])
    def non_detail_action(self, request):
        return Response({})  # wrong
