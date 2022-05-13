from audoma_api.models import (
    Account,
    Auction,
)
from audoma_api.permissions import (
    AlternatePermission1,
    AlternatePermission2,
    DetailPermission,
    ViewAndDetailPermission,
    ViewPermission,
)
from audoma_api.serializers import (
    AccountModelSerializer,
    AuctionModelSerializer,
    ExampleSerializer,
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

    @action(detail=True, methods=["post"])
    def detail_action(self, request, pk=None):
        return Response({})  # wrong

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
