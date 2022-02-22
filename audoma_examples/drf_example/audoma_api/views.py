from cgitb import lookup
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from audoma.drf import mixins
from audoma.drf import viewsets
from audoma_api.permissions import AlternatePermission2
from audoma_api.permissions import DetailPermission
from audoma_api.permissions import AlternatePermission1
from audoma_api.permissions import ViewAndDetailPermission
from audoma_api.permissions import ViewPermission
from audoma_api.serializers import ExampleSerializer
from audoma_api.serializers import ExampleModelSerializer
from audoma_api.models import ExampleModel
from audoma.drf.filters import DocumentedTypedChoiceFilter
from django_filters import rest_framework as df_filters
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema


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


example_choice = DocumentedTypedChoiceFilter(
    ExampleModel.EXAMPLE_CHOICES,
    'choice',
    lookup_expr='exact',
    field_name='choices'
)


class ExampleChoiceFilter(df_filters.FilterSet):
    choice = example_choice

    class Meta:
        model = ExampleModel
        fields = ['choice', ]


@method_decorator(name='list', decorator=swagger_auto_schema(
    manual_parameters=[example_choice.create_openapi_description()]))
class ExampleModelViewSet(
        mixins.ActionModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [
        IsAuthenticated, ViewAndDetailPermission, DetailPermission, ViewPermission,
        AlternatePermission1 | AlternatePermission2
    ]

    serializer_class = ExampleModelSerializer
    queryset = ExampleModel.objects.all()

    @action(detail=True, methods=['post'])
    def detail_action(self, request, pk=None):
        return Response({})  # wrong

    @action(detail=False, methods=['post'])
    def non_detail_action(self, request):
        return Response({})  # wron
