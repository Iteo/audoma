from car_api.models import (
    Car,
    CarRent,
    Customer,
    Manufacturer,
    Salesman,
)
from car_api.serializers import (
    CarCreateSerializer,
    CarDetailSerializer,
    CarListSerializer,
    CarRentResultSerializer,
    CarRentWriteSerializer,
    CustomerSerializer,
    ManufacturerSerializer,
    SalesmanDetailSerializer,
    SalesmanListSerializer,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from audoma.drf import (
    mixins,
    viewsets,
)


class CarRentViewset(
    mixins.ActionModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    collect_serializer_class = CarRentWriteSerializer
    result_serializer_class = CarRentResultSerializer


class SalesmanViewset(
    mixins.ActionModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    list_serializer_class = SalesmanListSerializer
    salesman_upgrade_serializer_class = SalesmanDetailSerializer

    @action(detail=True, methods=["post"])
    def salesman_upgrade(self, request, pk, *args, **kwargs):
        data = request.data.copy()
        data["user__id"] = pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.instnace, status_code=200)
