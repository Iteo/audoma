from audoma_api.models import (
<<<<<<< HEAD
    ExampleFileModel,
=======
    ExampleDependedModel,
>>>>>>> PINT-22: added search field explicit description
    ExampleModel,
)
from audoma_api.permissions import (
    AlternatePermission1,
    AlternatePermission2,
    DetailPermission,
    ViewAndDetailPermission,
    ViewPermission,
)
from audoma_api.serializers import (
<<<<<<< HEAD
    ExampleFileModelSerializer,
=======
    ExampleDependedModelSerializer,
>>>>>>> PINT-22: added search field explicit description
    ExampleModelSerializer,
    ExampleSerializer,
)
from django_filters import rest_framework as df_filters
from rest_framework.decorators import action
<<<<<<< HEAD
from rest_framework.parsers import MultiPartParser
=======
from rest_framework.filters import SearchFilter
>>>>>>> PINT-22: added search field explicit description
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
    choices = example_choice

    class Meta:
        model = ExampleModel
        fields = [
            "choices",
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

    @action(detail=True, methods=["post"])
    def detail_action(self, request, pk=None):
        return Response({})  # wrong

    @action(detail=False, methods=["post"])
    def non_detail_action(self, request):
        return Response({})  # wron


<<<<<<< HEAD
class ExampleFileUploadViewSet(
    mixins.ActionModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ExampleFileModelSerializer
    queryset = ExampleFileModel.objects.all()

    parser_classes = [MultiPartParser]
=======
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


class ExampleRelatedModelsViewSet(
    mixins.ActionModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):

    queryset = ExampleDependedModel.objects.none()
    serializer_class = ExampleDependedModelSerializer

    filter_backends = [SearchFilter, df_filters.DjangoFilterBackend]
    filterset_fields = [
        "foreign_key__name",
    ]
    search_fields = ["foreign_key__name", "name"]
>>>>>>> PINT-22: added search field explicit description
