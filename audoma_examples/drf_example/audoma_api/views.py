from audoma_api.models import (
    ExampleFileModel,
    ExampleModel,
)
from audoma_api.exceptions import (
    CustomBadRequestException,
    CustomConflictException,
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
    ExampleModelCreateSerializer,
    ExampleModelSerializer,
    ExampleSerializer,
    ExampleOneFieldSerializer
)
from django_filters import rest_framework as df_filters
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from audoma.drf import (
    mixins,
    viewsets,
)
from audoma.drf.decorators import audoma_action
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

    @audoma_action(detail=True, methods=['get'], responses={
            'get': "GET method is not allowed"
        }, collectors=None
    )
    def detail_action(self, request, pk=None):
        return Response({})  # wrong

    @action(detail=False, methods=['post'])
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


class ExampleModelPermissionLessViewSet(
    mixins.ActionModelMixin, viewsets.GenericViewSet
):
    serializer_class = ExampleModelSerializer
    queryset = ExampleModel.objects.all()

    @audoma_action(
        detail=True,
        methods=["post"],
        collectors={"post": ExampleModelCreateSerializer},
        responses={
            "post": {201: ExampleModelSerializer, 202: ExampleOneFieldSerializer}
        },
    )
    def detail_action(self, request, collect_serializer, pk=None):
        if request.data.pop("usertype", None):
            return collect_serializer.save(), 201
        return {"rate": ExampleOneFieldSerializer.RATE_CHOICES.LIKE}, 202

    @audoma_action(detail=False, methods=['get'], responses={'get': 'This is a test view'})
    def non_detail_action(self, request):
        return None, 200

    @audoma_action(
        detail=False, methods=['post'], responses=ExampleOneFieldSerializer, 
        collectors=ExampleOneFieldSerializer
    )
    def rate_create_action(
        self, request, collect_serializer
    ):
        return collect_serializer.save(), 201

    @audoma_action(detail=True, methods=["get"], responses=ExampleOneFieldSerializer)
    def specific_rate(self, request, pk=None):
        return {"rate": 1}, 200

    @audoma_action(
        detail=False,
        methods=["get"],
        responses=ExampleOneFieldSerializer,
        errors=[CustomBadRequestException(), CustomConflictException()],
    )
    def properly_defined_exception_example(self, request):
        raise CustomConflictException

    @audoma_action(detail=False, methods=["get"])
    def proper_usage_of_common_errors(self, request):
        raise NotFound

    @audoma_action(
        detail=False,
        methods=["get"],
        responses=ExampleOneFieldSerializer,
    )
    def improperly_defined_exception_example(self, request):
        raise CustomBadRequestException
