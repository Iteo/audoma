from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
from decimal import Decimal

from audoma_api.exceptions import (
    CustomBadRequestException,
    CustomConflictException,
)
from audoma_api.models import (
    Car,
    ExampleFileModel,
    ExampleModel,
    ExamplePerson,
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
    ExampleModelCreateSerializer,
    ExampleModelSerializer,
    ExampleOneFieldSerializer,
    ExamplePersonModelSerializer,
    ExampleSerializer,
    ManufacturerModelSerializer,
    MutuallyExclusiveExampleSerializer,
)
from django_filters import rest_framework as df_filters
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from audoma.decorators import audoma_action
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

    @audoma_action(
        detail=True,
        methods=["get"],
        results={"get": "GET method is not allowed"},
        collectors=None,
    )
    def detail_action(self, request, pk=None):
        return Response({})  # wrong

    @action(detail=False, methods=["post"])
    def non_detail_action(self, request):
        return Response({})  # wron


class ExamplePersonModelViewSet(
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
    ]

    serializer_class = ExamplePersonModelSerializer
    queryset = ExamplePerson.objects.all()

    @action(detail=True, methods=["post"])
    def detail_action(self, request, pk=None):
        return Response({})

    @action(detail=False, methods=["post"])
    def non_detail_action(self, request):
        return Response({})


class ExampleFileUploadViewSet(
    mixins.ActionModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ExampleFileModelSerializer
    queryset = ExampleFileModel.objects.all()

    parser_classes = [MultiPartParser]


class ManufacturerViewSet(
    mixins.ActionModelMixin,
    mixins.BulkCreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.BulkUpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Manufacturer.objects.all()
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

    filterset_fields = ["engine_type"]
    search_fields = ["=manufacturer", "name"]


class MutuallyExclusiveViewSet(
    mixins.ActionModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MutuallyExclusiveExampleSerializer


class ExampleModelPermissionLessViewSet(
    mixins.ActionModelMixin, viewsets.GenericViewSet
):
    serializer_class = ExampleModelSerializer
    queryset = ExampleModel.objects.all()

    @audoma_action(
        detail=True,
        methods=["post"],
        collectors={"post": ExampleModelCreateSerializer},
        results={"post": {201: ExampleModelSerializer, 202: ExampleOneFieldSerializer}},
    )
    def detail_action(self, request, collect_serializer, pk=None):
        if request.data.pop("usertype", None):
            return collect_serializer.save(), 201
        return {"rate": ExampleOneFieldSerializer.RATES.LIKE}, 202

    @audoma_action(
        detail=False,
        methods=["get"],
        results={"get": {200: "This is a test view", 404: "Not found"}},
    )
    def non_detail_action(self, request):
        return None, 200

    @audoma_action(
        detail=False,
        methods=["post"],
        results=ExampleOneFieldSerializer,
        collectors=ExampleOneFieldSerializer,
    )
    def rate_create_action(self, request, collect_serializer):
        return collect_serializer.save(), 201

    @audoma_action(detail=True, methods=["get"], results=ExampleOneFieldSerializer)
    def specific_rate(self, request, pk=None):
        return {"rate": ExampleOneFieldSerializer.RATES.DISLIKIE}, 200

    @audoma_action(
        detail=False,
        methods=["get"],
        results=ExampleOneFieldSerializer,
        errors=[CustomBadRequestException(), CustomConflictException],
    )
    def properly_defined_exception_example(self, request):
        raise CustomConflictException("Some custom message, that should be accepted")

    @audoma_action(detail=False, methods=["get"])
    def proper_usage_of_common_errors(self, request):
        raise NotFound

    @audoma_action(
        detail=False,
        methods=["get"],
        results=ExampleOneFieldSerializer,
    )
    def improperly_defined_exception_example(self, request):
        raise CustomBadRequestException

    def get_queryset(self):
        return ExampleModel.objects.none()

    def get_object(self):
        return ExampleModel(
            char_field="TESTChar",
            phone_number="+18888888822",
            email="test@iteo.com",
            url="http://localhost:8000/redoc/",
            boolean=False,
            nullboolean=None,
            mac_adress="96:82:2E:6B:F5:49",
            slug="tst",
            uuid="14aefe15-7c96-49b6-9637-7019c58c25d2",
            ip_address="192.168.10.1",
            integer=16,
            _float=12.2,
            decimal=Decimal("13.23"),
            datetime=datetime(2009, 11, 13, 10, 39, 35),
            date=date(2009, 11, 13),
            time=time(10, 39, 35),
            duration=timedelta(days=1),
            choices=1,
            json="",
        )

    @audoma_action(
        detail=True,
        methods=["put", "patch"],
        collectors=ExampleModelCreateSerializer,
        results=ExampleModelSerializer,
    )
    def example_update_action(self, request, collect_serializer, pk=None):
        return collect_serializer.save(), 201

    @audoma_action(
        detail=False, many=True, methods=["get"], results=ExamplePersonModelSerializer
    )
    def example_many_test_action(self, request):
        instance = ExamplePerson.objects.none()
        return instance, 200
