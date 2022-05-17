from datetime import timedelta
from decimal import Decimal

from audoma_api.exceptions import (
    CustomConflictException,
    CustomValidationErrorException,
)
from audoma_api.models import (
    Account,
    Auction,
    Car,
    ExampleSimpleModel,
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
    AccountCreateSerializer,
    AccountModelSerializer,
    AuctionModelSerializer,
    CarModelSerializer,
    ExampleSerializer,
    ExampleSimpleModelSerializer,
    ManufacturerModelSerializer,
    MutuallyExclusiveExampleSerializer,
    RateSerializer,
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


account_type_choices = DocumentedTypedChoiceFilter(
    Account.ACCOUNT_TYPE, "account_type", lookup_expr="exact", field_name="choices"
)


class AccountTypeFilter(df_filters.FilterSet):
    choice = account_type_choices

    class Meta:
        model = Account
        fields = [
            "choice",
        ]


class AccountViewSet(
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

    filterset_class = AccountTypeFilter
    serializer_class = AccountModelSerializer
    queryset = Account.objects.all()

    @audoma_action(
        detail=True,
        methods=["post"],
        collectors={"post": AccountCreateSerializer},
        results={"post": {201: AccountCreateSerializer, 202: RateSerializer}},
    )
    def detail_action(self, request):
        return Response({})

    @action(detail=False, methods=["post"])
    def non_detail_action(self, request):
        return Response({})  # wron


class AuctionViewSet(
    mixins.ActionModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AuctionModelSerializer
    queryset = Auction.objects.all()

    parser_classes = [MultiPartParser]


class AnonymousAccountViewSet(mixins.ActionModelMixin, viewsets.GenericViewSet):
    serializer_class = AccountModelSerializer
    queryset = Account.objects.none()

    @audoma_action(
        detail=False,
        methods=["post"],
        collectors={"post": AccountCreateSerializer},
        results={
            "post": {201: AccountModelSerializer},
        },
        errors=[CustomValidationErrorException],
    )
    def create_account(self, request, collect_serializer):
        # username can't be username
        if request.data.get("username", None).lower() != "username":
            return collect_serializer.save(), 201
        raise CustomValidationErrorException("This username is not allowed.")

    @audoma_action(
        detail=False,
        methods=["post", "get"],
        results={"get": {200: AccountModelSerializer}, "post": {201: RateSerializer}},
        collectors=RateSerializer,
        errors=[CustomValidationErrorException, CustomConflictException],
    )
    def rate_profile(self, request, collect_serializer):
        if request.method.lower() == "get":
            return Account(), 200

        if len(request.data.keys()) > 1:
            raise CustomConflictException("Too many keys")

        return collect_serializer.save(), 201

    @audoma_action(
        detail=False,
        methods=["get"],
        results=RateSerializer,
        errors=[CustomConflictException("Some random conflict exception")],
    )
    def improperly_defined_exception_example(self, request):
        raise CustomConflictException()

    @audoma_action(detail=True, methods=["get"], results=RateSerializer)
    def view_specific_rate(self, request, pk=None):
        if int(pk) == 0:
            # Proper usage of common errors
            raise NotFound
        return {"rate": RateSerializer.RATES.DISLIKE}, 200

    def get_object(self):
        return Account(
            username="Username",
            first_name="First",
            last_name="Last",
            phone_number="+18888888822",
            nationality="SomeNationality",
            city="RandomCity",
            email="test@iteo.com",
            bio="LoremIpsum",
            is_active=True,
            mac_adress="96:82:2E:6B:F5:49",
            ip_address="192.168.10.1",
            age=16,
            _float=12.2,
            decimal=Decimal("13.23"),
            duration=timedelta(days=1),
            account_type=Account.ACCOUNT_TYPE.FACEBOOK,
            account_balance=0,
        )

    @audoma_action(
        detail=True,
        methods=["put", "patch"],
        collectors=AccountCreateSerializer,
        results=AccountModelSerializer,
    )
    def update_profile(self, request, collect_serializer, pk=None):
        return collect_serializer.save(), 201


class CarChoiceFilter(df_filters.FilterSet):
    class Meta:
        model = Car
        fields = ["engine_size", "body_type"]


class ManufacturerViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Manufacturer.objects.none()
    serializer_class = ManufacturerModelSerializer

    filter_backends = [SearchFilter, df_filters.DjangoFilterBackend]

    filterset_fields = [
        "slug_name",
    ]
    search_fields = ["=slug_name", "name"]


class CarViewSet(
    mixins.ActionModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Car.objects.none()
    serializer_class = CarModelSerializer
    filterset_class = CarChoiceFilter


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


class MutuallyExclusiveViewSet(
    mixins.ActionModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MutuallyExclusiveExampleSerializer
