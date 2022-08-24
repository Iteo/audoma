from car_api.models import (
    Car,
    CarRent,
    Customer,
    Manufacturer,
    Salesman,
)

from audoma.drf import serializers


class ManufacturerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ["name", "slug_name"]


class ManufacturerBulkCreateSerializer(serializers.ModelSerializer):
    ...


class CarDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = [
            "manufacturer__name",
            "name",
            "body_type",
            "engine_size",
            "engine_size",
        ]


class CarListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ["manufacturer__name", "name", "body_type"]


class CarCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = [
            "manufacturer__name",
            "name",
            "body_type",
            "engine_size",
            "engine_size",
        ]


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["name", "phone", "user__email"]


class CarRentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarRent
        fields = ["car", "rent_start", "rent_end", "customer"]


class CarRentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarRent
        fields = ["car", "rent_start", "rent_end", "customer"]

    def save(self, *args, **kwargs):
        request = self.context["request"]
        instance = super().save(*args, **kwargs)
        # retrieve salesman
        sales = Salesman.objects.get(user=request.user)
        instance.rented_by = sales
        instance.save()
        return instance


class SalesmanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salesman
        fields = ["name", "user__email", "phone"]


class SalesmanDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salesman
        fields = ["name", "user", "phone", "rented_cars_number"]
