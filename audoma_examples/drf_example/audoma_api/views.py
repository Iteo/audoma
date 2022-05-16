from audoma_api.models import (
    Car,
    ExampleDependedModel,
    ExampleFileModel,
    ExampleForeignKeyModel,
    ExampleModel,
    Manufacturer,
)
from audoma_api.permissions import (
    AlternatePermission1,
    AlternatePermission2,
    DetailPermission,
    ViewAndDetailPermission,
    ViewPermission,
)
from audoma_api.serializers import (
    CarModelSerializer,
    ExampleFileModelSerializer,
    ExampleModelSerializer,
    ExampleSerializer,
    ManufacturerModelSerializer,
)
from django_filters import rest_framework as df_filters
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.utils.decorators import method_decorator

from audoma.drf import (
    mixins,
    viewsets,
)
from audoma.drf.filters import DocumentedTypedChoiceFilter


class ExampleViewSet(
    mixins.ActionModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [
        IsAuthenticated,
        ViewAndDetailPermission,
        DetailPermission,
        ViewPermission,
        AlternatePermission1 | AlternatePermission2,
    ]
    # permission_classes = [
    #     IsAuthenticated, ViewAndDetailPermission, DetailPermission, ViewPermission,
    #     AlternatePermission1 | AlternatePermission2
    # ]

    serializer_class = ExampleSerializer
    queryset = {}

    @action(detail=True, methods=["post"])
    def detail_action(self, request, pk=None):
        return Response({})  # wrong

    @action(detail=False, methods=["post"])
    def non_detail_action(self, request):
        return Response({})  # wrong


example_choice = DocumentedTypedChoiceFilter(
    ExampleModel.EXAMPLE_CHOICES, "choice", lookup_expr="exact", field_name="choices"
)


class ExampleChoiceFilter(df_filters.FilterSet):
    choice = example_choice

    class Meta:
        model = ExampleModel
        fields = [
            "choice",
        ]


class ExampleModelViewSet(
    mixins.ActionModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):

    permission_classes = [
        IsAuthenticated,
        ViewAndDetailPermission,
        DetailPermission,
        ViewPermission,
        AlternatePermission1 | AlternatePermission2,
    ]

    filterset_class = ExampleChoiceFilter
    serializer_class = ExampleModelSerializer
    queryset = ExampleModel.objects.all()

    def list(self, request):
        return Response({})

    @action(detail=True, methods=["get"])
    def detail_action(self, request, pk=None):
        return Response({})  # wrong

    @action(detail=False, methods=["post"])
    def non_detail_action(self, request):
        return Response({})  # wron


class ExampleFileUploadViewSet(
    mixins.ActionModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ExampleFileModelSerializer
    queryset = ExampleFileModel.objects.all()

    parser_classes = [MultiPartParser]


class ExampleDefaultChoiceFilter(df_filters.FilterSet):
    class Meta:
        model = ExampleModel
        fields = [
            "choices",
        ]


class ExampleFiltersetClassViewset(
    mixins.ActionModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    filterset_class = ExampleDefaultChoiceFilter
    serializer_class = ExampleModelSerializer
    queryset = ExampleModel.objects.all()


class ExampleFiltersetFieldsViewset(
    mixins.ActionModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    filterset_fields = [
        "choices",
    ]
    serializer_class = ExampleModelSerializer
    queryset = ExampleModel.objects.all()


class ManufacturerViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Manufacturer.objects.none()
    serializer_class = ManufacturerModelSerializer


class CarViewSet(
    mixins.ActionModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Car.objects.none()
    serializer_class = CarModelSerializer

    filter_backends = [SearchFilter, df_filters.DjangoFilterBackend]

    filterset_fields = [
        "engine_size",
    ]
    search_fields = ["=manufacturer", "name"]
