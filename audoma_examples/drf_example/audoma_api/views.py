from audoma_api.models import (
    ExampleFileModel,
    ExampleModel,
    ExampleSimpleModel,
)
from audoma_api.permissions import (
    AlternatePermission1,
    AlternatePermission2,
    DetailPermission,
    ViewAndDetailPermission,
    ViewPermission,
)
from audoma_api.serializers import (
    ExampleFileModelSerializer,
    ExampleModelSerializer,
    ExampleSerializer,
    ExampleSimpleModelSerializer,
)
from django_filters import rest_framework as df_filters
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
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

    @action(detail=True, methods=["post"])
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


class ExampleSimpleModelViewSet(
    mixins.ListModelMixin,
    mixins.BulkCreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.BulkUpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ExampleSimpleModelSerializer

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return ExampleSimpleModel.objects.all()

    # def get_serializer(self, *args, **kwargs):
    #     ret = super().get_serializer(*args, **kwargs)
    #     print(ret)
    #     return ret

    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)
