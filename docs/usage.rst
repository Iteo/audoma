======
Usage
======

.. _get_serializer_class:

Viewset defined serializers
============================

Serializer class custom configs
--------------------------------

| By, default Django Rest Framework provides two methods to get a serializer:
| `get_serializer` and `get_serializer_class`.
| Those methods check if `self` has the property called `serializer_class`
| and returns it or its instance.

| Audoma Extends this behavior by, first of all, enabling to
| define `collect` and `result` serializer for given views, for all actions.

| Example:

.. code-block :: python
   :linenos:

    from audoma.drf import viewsets
    from audoma.drf import mixins
    from example_app.serializers import (
        MyCollectSerializer,
        MyResultSerializer
    )

    class MyViewSet(
        mixins.ActionModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet
    ):
        collect_serializer_class = MyCollectSerializer
        result_serializer_class = MyResultSerializer

| It is also possible to define a custom serializer for each action in the viewset.
| This is possible for generic drfs' actions and also for custom actions,
| created with `@action` decorator.

| Example:

.. code-block :: python
   :linenos:

    from rest_framework.decorators import action
    from rest_framework.response import Response

    from audoma.drf import viewsets
    from audoma.drf import mixins
    from example_app.serializers import (
        MyCreateSerializer,
        MyCustomActionSerializer
    )

    class MyViewSet(
        mixins.ActionModelMixin,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet
    )::
        create_serializer_class = MyCreateSerializer
        custom_action_serializer_class = MyCustomActionSerializer

        @action(detail=True, methods=["post"])
        def custom_action(self, request):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.instance, status_code=200)

| It is also possible for action to serve more than one http method.
| In audoma it is allowed to assign different serializers for each of actions methods.
| This may be usefull for example if you want to use different list post serializer
| and list get serializer.

| Example:

.. code-block :: python
   :linenos:

    from audoma.drf import viewsets
    from audoma.drf import mixins
    from example_app.serializers import (
        MyCreateSerializer,
        MyCustomActionSerializer
    )

    class MyViewSet(
        mixins.ActionModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet
    ):
        get_list_serializer_class = MyListSerializer
        post_list_serializer_class = MyBulkCreateSerializer


| Each action may also define different `collect` and `result` serializer.

| Example:

.. code-block :: python
   :linenos:

    from rest_framework.decorators import action
    from rest_framework.response import Response

    from audoma.drf import viewsets
    from example_app.serializers import (
        MyCreateSerializer,
        MyCustomActionSerializer
    )

    class MyViewSet(
        mixins.ActionModelMixin,
        viewsets.GenericViewSet
    ):
        custom_action_collect_serializer = MyModelCreateSerializer
        custom_action_result_serializer = MyModelSerializer

        @action(detail=True, methods=["post"])
        def custom_action(self, request):
            serializer = self.get_serializer(data=request.data, serializer_type="collect")
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_serializer = self.get_result_serializer(instance=serializer.instance)
            return Response(response_serializer.data, status_code=201)

| The most atomic way of defining serializer classes in audoma is to define serializer
| per method, action and type.
| This means that each actions method will have `result` and `collect` serializers.

| Example:

.. code-block :: python
   :linenos:

    from rest_framework.decorators import action
    from rest_framework.response import Response

    from audoma.drf import viewsets
    from audoma.drf import mixins
    from example_app.serializers import (
        MyListSerializer,
        MySerializer,
        MyCreateSerializer
    )

    class MyViewSet(
        mixins.ActionModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet
    ):
        get_new_action_result_serializer_class = MyListSerializer
        post_new_action_result_serializer_class = MySerializer
        post_new_action_collect_serializer_class = MyCreateSerializer

        @action(detail=True, methods=["post", "get"])
        def new_action(self, request, *args, **kwargs):
            if request.method == "POST":
                serializer = self.get_serializer(data=request.data, serializer_type="collect")
                serializer.is_valid(raise_exception=True)
                serializer.save()
                instance = serializer.instance
            else:
                instance = self.get_object()
            response_serializer = self.get_result_serializer(instance=instance)
            return Response(response_serializer.data, status_code=201)


| As you surely presume, all of those serializer classes
| variables may be defined on one viewset at once
| Than those will be traversed in the defined order.
| The first one matching will be used.

| Let's take an example viewset:

.. code-block :: python
   :linenos:

    from rest_framework.decorators import action
    from rest_framework.response import Response

    from audoma.drf import viewsets
    from example_app.serializers import (
        MySerachCollectSerializer,
        MySearchResultSerializer,
        MyCountCreateSerializer,
        MyCountUpdateSerializer,
        MyCountResultSerializer,
        MyDefaultSerializer
    )
    from example_app.models import (
        MyModel,
        CountModel
    )


    class MyViewSet(
        mixins.ActionModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet,
    ):

        queryset = MyModel.objects.all()

        post_search_collect_serializer_class = MySerachCollectSerializer
        post_search_result_serializer_class = MySearchResultSerializer

        post_count_collect_serializer_class = MyCountCreateSerializer
        put_count_collect_serializer_class = MyCountUpdateSerializer
        count_result_serializer_class = MyCountResultSerializer

        serializer_class = MyDefaultSerializer

        def get_object(self, pk=None):
            return self.querset.get(pk=pk)

        @action(detail=False, methods=["post"])
        def search(self, request):
            serializer = self.get_serializer(data=request.data, serializer_type="collect")
            serializer.is_valid(raise_exception=True)
            serializer.save()
            result_serializer = self.get_result_serializer(instance=serializer.instance)
            return Response(result_serializer.data, status=201)

        @action(detail=True, methods=["post", "get", "put"])
        def count(self, request, *args, **kwargs):
        code = 200
            if request.method != "GET":
                serializer = self.get_serializer(data=request.data, serializer_type="collect")
                serializer.is_valid(raise_exception=True)
                serializer.save()
                instance = serializer.instance
                code = 201 if request.method == "POST"
            else:
                instance = CountModel.objects.get_count(slug=kwargs.pop("slug"))

            result_serializer = self.get_result_serializer(instance=instance)
            return Response(result_serializer.data, status=code)


| Let's examine the above example.
| Action search has two serializers defined, both are defined for post method.
| One of those will be used to collect data, other to return the result.
| In this case we may also simplify the serializer classes variable names,
| beacuse search only serves post method, so we may also name those variables like this:

.. code :: python

    ...
    search_collect_serializer_class = MySerachCollectSerializer
    search_result_serializer_class = MySearchResultSerializer
    ...

| This will work the same way as serializer classes defined in the example.

| For the `count` action we have defined three serializers.
| First two serializers handle collecting data for "`POST` and `PUT` HTTP methods.
| The third serializer is common for all seved by `count` action mehtods, it is a result serializer.
| No matter which method we will use, this is the serializer which will be used to return the result.
| In this case, if there won't be further changes in `count` action
| we may define `count_result_serializer_class` as `count_serializer_class`.
| This will work the same way because of the traverse order defined in audoma.
| But this solution may be problematic during introducing any changes.

.. code :: python

    ...
    post_count_collect_serializer_class = MyCountCreateSerializer
    put_count_collect_serializer_class = MyCountUpdateSerializer
    count_serializer_class = MyCountResultSerializer
    ...

| The one last thing that left in this viewset is `serializer_class`.
| This variable will be used by all other actions supported by thise viewset.
| In the viewset definition there are few mixin classes passed, so those will
| provide some basic functionalities to our viewset.

| If this is going to be necessary it is possible to create sepparate serializer for those actions also.

| Example:

.. code-block :: python
   :linenos:

    from rest_framework.decorators import action
    from rest_framework.response import Response

    from audoma.drf import viewsets
    from example_app.serializers import (
        MySerachCollectSerializer,
        MySearchResultSerializer,
        MyCountCreateSerializer,
        MyCountUpdateSerializer,
        MyCountResultSerializer,
        MyDefaultSerializer,
        MyListSerializer,
        MyCreateSerializer
    )
    from example_app.models import (
        MyModel,
        CountModel
    )


    class MyViewSet(
        mixins.ActionModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet,
    ):

        queryset = MyModel.objects.all()

        post_search_collect_serializer_class = MySerachCollectSerializer
        post_search_result_serializer_class = MySearchResultSerializer

        post_count_collect_serializer_class = MyCountCreateSerializer
        put_count_collect_serializer_class = MyCountUpdateSerializer
        count_result_serializer_class = MyCountResultSerializer

        list_serializer_class = MyListSerializer
        create_serializer_class = MyCreateSerializer
        serializer_class = MyDefaultSerializer

        def get_object(self, pk=None):
            return self.querset.get(pk=pk)

        @action(detail=False, methods=["post"])
        def search(self, request):
            serializer = self.get_serializer(data=request.data, serializer_type="collect")
            serializer.is_valid(raise_exception=True)
            serializer.save()
            result_serializer = self.get_result_serializer(instance=serializer.instance)
            return Response(result_serializer.data, status=201)

        @action(detail=True, methods=["post", "get", "put"])
        def count(self, request, *args, **kwargs):
        code = 200
            if request.method != "GET":
                serializer = self.get_serializer(data=request.data, serializer_type="collect")
                serializer.is_valid(raise_exception=True)
                serializer.save()
                instance = serializer.instance
                code = 201 if request.method == "POST"
            else:
                instance = CountModel.objects.get_count(slug=kwargs.pop("slug"))

            result_serializer = self.get_result_serializer(instance=instance)
            return Response(result_serializer.data, status=code)

Serializer classes name traverse order
---------------------------------------
| After examining above examples, it is obious that there is some defined order
| while traversing defined variables. Variable which will be used as serializer
| class are being picked in this order:

* `{method}_{action}_{type}_serializer_class`
* `{action}_{type}_serializer_class`
* `{method}_{action}_serializer_class`
* `{action}_serializer_class`
* `common_{type}_serializer_class`
* `serializer_class`

| For all serializers defined this way, there is also support for proper documentation in api schema.

Permissions
===========

By default, in the `drf-spectacular` viewset permissions were not documented at all.
Currently, permissions are being documented for each viewset separately.

You don't have to define anything extra, this is being handled just out of the box.
The only thing it is required is to define permissions on your viewset.

Example:

.. code-block :: python
   :linenos:

    from rest_framework.decorators import action
    from rest_framework.response import Response

    from audoma.drf import viewsets
    from example_app.serializers import (
        MySerachCollectSerializer,
        MySearchResultSerializer,
        MyCountCreateSerializer,
        MyCountUpdateSerializer,
        MyCountResultSerializer,
        MyDefaultSerializer,
        MyListSerializer,
        MyCreateSerializer
    )
    from example_app.permissions import (
        AlternatePermission1,
        AlternatePermission2,
        DetailPermission,
        ViewAndDetailPermission,
        ViewPermission,
    )
    from example_app.models import (
        MyModel,
        CountModel
    )


    class MyViewSet(
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

        queryset = MyModel.objects.all()

        post_search_collect_serializer_class = MySerachCollectSerializer
        post_search_result_serializer_class = MySearchResultSerializer

        post_count_collect_serializer_class = MyCountCreateSerializer
        put_count_collect_serializer_class = MyCountUpdateSerializer
        count_result_serializer_class = MyCountResultSerializer

        list_serializer_class = MyListSerializer
        create_serializer_class = MyCreateSerializer
        serializer_class = MyDefaultSerializer

        def get_object(self, pk=None):
            return self.querset.get(pk=pk)

        @action(detail=False, methods=["post"])
        def search(self, request):
            serializer = self.get_serializer(data=request.data, serializer_type="collect")
            serializer.is_valid(raise_exception=True)
            serializer.save()
            result_serializer = self.get_result_serializer(instance=serializer.instance)
            return Response(result_serializer.data, status=201)

        @action(detail=True, methods=["post", "get", "put"])
        def count(self, request, *args, **kwargs):
        code = 200
            if request.method != "GET":
                serializer = self.get_serializer(data=request.data, serializer_type="collect")
                serializer.is_valid(raise_exception=True)
                serializer.save()
                instance = serializer.instance
                code = 201 if request.method == "POST"
            else:
                instance = CountModel.objects.get_count(slug=kwargs.pop("slug"))

            result_serializer = self.get_result_serializer(instance=instance)
            return Response(result_serializer.data, status=code)

| Currently there is no way to cosutomize this behaviour in audoma.

.. _choices:

Custom choices
==============
| Audoma provides new way of defining choices and new choices class
| which allows to call choice by it's name.\

| Example definition and usage:

.. code-block :: python
   :linenos:

    from audoma.django.db import models
    from audoma.choices import make_choices


    class CarModel(models.Model):


        CAR_BODY_TYPES = make_choices(
            "BODY_TYPES",
            (
                (1, "SEDAN", "Sedan"),
                (2, "COUPE", "Coupe"),
                (3, "HATCHBACK", "Hatchback"),
                (4, "PICKUP", "Pickup Truck"),
            ),
        )

        name = models.CharField(max_length=255)
        body_type = models.IntegerField(choices=CAR_BODY_TYPES.get_choices())

        engine_size = models.FloatField()

        def is_sedan(self):
            return self.body_type is BODY_TYPE_CHOICES.SEDAN

| Additionally it's worth mention that those choices will be shown in docs in fields' description.
| Those will also appear in schema as x-choices.

# TODO - add ref
# TODO - verify x-choices


Filters
=======

Default Filters
----------------

| In `drf`, it's possible to define `filterset_fields` and `filterset_class`.
| By default, `drf-spectacular`` supports `django-filters`. Which are being documented.
| Audoma has been tested with default drfs filter backend and `DjangoFilterBackend`.
| For more accurate documentation, we recommend using `DjangoFilterBackend` as the default one.
| Filters and search fields are being documented out of the box automatically.

| Example:

.. code-block :: python
   :linenos:

    from rest_framework.filters import SearchFilter
    from audoma.drf import mixins
    from audoma.drf import viewsets
    from django_filters import rest_framework as df_filters

    from example_app.models import CarModel
    from example_app.serializers import CarModelSerializer

    class CarViewSet(
        mixins.ActionModelMixin,
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet,
    ):
        queryset = CarModel.objects.all()
        serializer_class = CarModelSerializer

        filter_backends = [SearchFilter, df_filters.DjangoFilterBackend]

        filterset_fields = ["body_type"]
        search_fields = ["=manufacturer", "name"]


| It is also possible to define the `filterset` class which will also be documented
| without any additional steps.

.. code-block :: python
   :linenos:

    from rest_framework.filters import SearchFilter
    from audoma.drf import mixins
    from audoma.drf import viewsets
    from django_filters import rest_framework as df_filters

    from example_app.models import CarModel
    from example_app.serializers import CarModelSerializer


    class CarFilter(df_filters.FilterSet):
        body_type = df_filters.TypedChoiceFilter(
            Car.CAR_BODY_TYPES.get_choices(), "body_type",
            lookup_expr="exact", field_name="body_type"
        )

        class Meta:
            model = CarModel
            fields = [
                "body_type",
            ]


    class CarViewSet(
        mixins.ActionModelMixin,
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet,
    ):
        queryset = CarModel.objects.all()
        serializer_class = CarModelSerializer

        filter_backends = [SearchFilter, df_filters.DjangoFilterBackend]

        filterset_class = CarFilter
        search_fields = ["=manufacturer", "name"]

| Audoma extends documenting filters by two main features.

| Additional enum documentation in field description:
| In `drf-spectacular`, enums are being shown only as values possible to pass to the filter.
| With audoma you also get a display field of a choice, this may be useful to show display value
| in a drop-down for example. This is being shown as mapping value - field

# TODO - image


| The next feature is schema extension which is not visible in swagger or redoc frontend.
| This schema extension is :ref:`x-choices`. Which provides mapping for filter values.
| Passing x-choices in schema allows frontend developer to use mapping to show display/value fields
| without looking into field description.


Validators
===========

ExclusiveFieldsValidator
--------------------------

| This is an additional validator, which allows defining mutually exclusive fields in the serializer.
| It validates if any of the fields have been given and if not all exclusive fields have been given.

| This validator takes params:

* fields - list or a tuple of field names
* message - string message, which will replace default validator message
* required - boolean which determines if any of the fields must be given
* message_required - a message which will be displayed if one of the fields is required,
    and none has been passed

| Usage is quite simple:

.. code-block :: python
   :linenos:

    from audoma.drf import serializers
    from audoma.drf.validators import ExclusiveFieldsValidator


    class MutuallyExclusiveExampleSerializer(serializers.Serializer):
        class Meta:

            validators = [
                ExclusiveFieldsValidator(
                    fields=[
                        "example_field",
                        "second_example_field",
                    ]
                ),
            ]

        example_field = serializers.CharField(required=False)
        second_example_field = serializers.CharField(required=False)


Decorators
===========

@extend_schema_field
---------------------

| This decorator is by default `drf-spectacular` decorator.
| Audoma only changes its behaviour, in `drf-spectacular` using this decorator casued overriding
| all informations about field. Audoma does not override information, it only updates available informations
| with those passed to the decorator.

| This may be very useful while defining examples.
| We don't want to erase all other field informations
| just because we want to define example for this field.
| Also passing all field information  additionally just because we want
| to define example seems unneccessary and redundant.

| Example:

.. code-block :: python
   :linenos:

    from audoma.drf.fields import FloatField

    from drf_spectacular.utils import extend_schema_field

    @extend_schema_field(
        field={
            "example": 10.00
        }
    )
    class CustomExampleFloatField(FloatField):
        pass

| Above we simply add default example for all
| fields which will be of class `CustomExampleFloatField`.


@audoma_action
---------------
| This is one of the most complex features offered by audoma.
| In fact this is an extension of action decorator, which by default is Django Rest Framewok functionality.
| It also allows registering custom action for viewset.
| In case of `audoma_action`, it is also possible to define additional parameters, such as:

Usage
^^^^^^

| Let's take an example vieset:

.. code-block :: python
   :linenos:

    from audoma.drf import mixins
    from audoma.drf import viewsets

    from app.serializers import (
        CarListSerializer,
        CarWriteSerializer,
        CarDetailsSerializer,
        CarCrateRateSerializer,
        CarRateSerializer
    )
    from app.models import (
        Car,
        CarRate
    )


    class CarViewSet(
        mixins.ActionModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
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

        create_collect_serializer_class = CarWriteSerializer
        create_result_serializer_class = CarDetailsSerializer
        retrieve_serializer_class = CarDetailsSerializer
        list_serializer_class = CarListSerializer

        queryset = {}
        @audoma_action(
            detail=True,
            methods=["get", "post"]
            collectors=CarCreateRateSerialzer,
            results=CarRateSerializer,
            errors=[CustomCarRateException]
        )
        def rate(self, request, pk=None, *args, **kwargs):
            if request.method == "POST":
                collect_serializer = kwargs.pop("collect_serializer")
                instance = collect_serializer.save()
            else:
                instance = CarRate.objects.get_random_car_rate(car_pk=pk)
            return instance, 200

| Let's examine the above example.
| We've created the viewset with some initial actions served, and serializers assigned to those actions.

| Next we've defined new custom action calle `rate`.
| This action serves `get` and `post` methods, in case of this action '
| we use single result and collect serializers.

| As you may see, `audoma_action` method does not return default response, it returns
| instance and status_code, the `audoma_action` decorator takes care
| of creating the response from this.

| Let's modify our example, let there be a custom exception risen.

.. code-block :: python
   :linenos:

    from audoma.drf import mixins
    from audoma.drf import viewsets
    from rest_framework.exceptions import APIException

    from app.serializers import (
        CarListSerializer,
        CarWriteSerializer,
        CarDetailsSerializer,
        CarCrateRateSerializer,
        CarRateSerializer
    )
    from app.models import (
        Car,
        CarRate
    )


    class CustomCarRateException(APIException):
        default_detail = "Error during retrieving car rate!"
        status_code = 500


    class CarViewSet(
        mixins.ActionModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
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

        create_collect_serializer_class = CarWriteSerializer
        create_result_serializer_class = CarDetailsSerializer
        retrieve_serializer_class = CarDetailsSerializer
        list_serializer_class = CarListSerializer

        queryset = {}

        @audoma_action(
            detail=True,
            methods=["get", "post"]
            collectors=CarCreateRateSerialzer,
            results=CarRateSerializer,
            errors=[CustomCarRateException]
        )
        def rate(self, request, pk=None, *args, **kwargs):
            if request.method == "POST":
                collect_serializer = kwargs.pop("collect_serializer")
                instance = collect_serializer.save()
            else:
                instance = CarRate.objects.get_random_car_rate(car_pk=pk)
                if not instance:
                    raise CustomCarRateException
            return instance, 200

| After this change it is possible to rise any exception of type `CustomCarRateException` in rate action.
| Also this exception will be documented in this action schema.

| Let's presume that we now want to return status code `201` and rate instance on `post`,
| but on `get` we want to return car instance with random rate and status code `200`.

.. code-block :: python
   :linenos:

    from audoma.drf import mixins
    from audoma.drf import viewsets
    from rest_framework.exceptions import APIException

    from app.serializers import (
        CarListSerializer,
        CarWriteSerializer,
        CarDetailsSerializer,
        CarCrateRateSerializer,
        CarRateSerializer
    )
    from app.models import (
        Car,
        CarRate
    )


    class CustomCarException(APIException):
        default_detail = "Car can't be found"
        status_code = 500


    class CarViewSet(
        mixins.ActionModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
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

        create_collect_serializer_class = CarWriteSerializer
        create_result_serializer_class = CarDetailsSerializer
        retrieve_serializer_class = CarDetailsSerializer
        list_serializer_class = CarListSerializer

        queryset = {}

        @audoma_action(
            detail=False,
            methods=["get", "post"]
            collectors=CarCreateRateSerialzer,
            results={"post":{201: CarRateSerializer}, "get":{200: CarDetailsSerializer}},
            errors=[CustomCarException]
        )
        def rate(self, request, *args, **kwargs):
            if request.method == "POST":
                collect_serializer = kwargs.pop("collect_serializer")
                instance = collect_serializer.save()
                return instance. 201
            else:
                instance = car.objects.get(pk=pk)
                if not instance:
                    raise CustomCarException
                return instance, 200

| Now we use different serializers for each method, depended on returned status code.
| Each of these serializer is using different model, `audoma_action` makes such situations super easy.


| Let's take different example, we have an action which should return string message, depends on
| current car state.

.. code-block :: python
   :linenos:

    from audoma.drf import mixins
    from audoma.drf import viewsets
    from rest_framework.exceptions import APIException

    from app.serializers import (
        CarListSerializer,
        CarWriteSerializer,
        CarDetailsSerializer,
        CarCrateRateSerializer,
        CarRateSerializer
    )
    from app.models import (
        Car,
        CarRate
    )


    class CustomCarException(APIException):
        default_detail = "Car can't be found"
        status_code = 500


    class CarViewSet(
        mixins.ActionModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
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

        create_collect_serializer_class = CarWriteSerializer
        create_result_serializer_class = CarDetailsSerializer
        retrieve_serializer_class = CarDetailsSerializer
        list_serializer_class = CarListSerializer

        queryset = {}

        @audoma_action(
            detail=False,
            methods=["get", "post"]
            collectors=CarCreateRateSerialzer,
            results={"post":{201: CarRateSerializer}, "get":{200: CarDetailsSerializer}},
            errors=[CustomCarException]
        )
        def rate(self, request, *args, **kwargs):
            if request.method == "POST":
                collect_serializer = kwargs.pop("collect_serializer")
                instance = collect_serializer.save()
                return instance. 201
            else:
                instance = car.objects.get(pk=pk)
                if not instance:
                    raise CustomCarException
                return instance, 200


        @audoma_action(
            detail=False,
            methods=["get"],
            results="Car is available"
        )
        def active(self, request, pk=None):
            instance = self.get_object(pk=pk)
            if instnace.active:
                return None, 200
            return "Car is unavailable", 200


| This action may return None, or string, but as you may see in results we have also string defined.
| The string defaut in the results it is a string which will be message returned by default.
| The default message will be returned if instance is None.
| If returned string instance won't be None, than the returned instance will be
| included in the response.

| While returning string message as an instnace, audoma simply wraps this message into `json`.
| Wrapped message would look like this:

.. code :: json

    {
        "message": "Car is available"
    }

| It's clear that we can combine those results, so in one action
| we may return string instance, and model instance.
| Let's modify our rate function, that it'll return default message if rating is disabled.

.. code-block :: python
   :linenos:

    from audoma.drf import mixins
    from audoma.drf import viewsets
    from rest_framework.exceptions import APIException
    from django.conf import settings

    from app.serializers import (
        CarListSerializer,
        CarWriteSerializer,
        CarDetailsSerializer,
        CarCrateRateSerializer,
        CarRateSerializer
    )
    from app.models import (
        Car,
        CarRate
    )


    class CustomCarException(APIException):
        default_detail = "Car can't be found"
        status_code = 500


    class CarViewSet(
        mixins.ActionModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
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

        create_collect_serializer_class = CarWriteSerializer
        create_result_serializer_class = CarDetailsSerializer
        retrieve_serializer_class = CarDetailsSerializer
        list_serializer_class = CarListSerializer

        queryset = {}

        @audoma_action(
            detail=False,
            methods=["get", "post"]
            collectors=CarCreateRateSerialzer,
            results={
                "post":{201: CarRateSerializer},
                "get":{200: CarDetailsSerializer, 204:"Rate service currently unavailable"}
            },
            errors=[CustomCarException]
        )
        def rate(self, request, *args, **kwargs):
            if settings.RATE_AVAILABLE:
                return None, 204

            if request.method == "POST":
                collect_serializer = kwargs.pop("collect_serializer")
                instance = collect_serializer.save()
                return instance. 201
            else:
                instance = car.objects.get(pk=pk)
                if not instance:
                    raise CustomCarException
                return instance, 200


        @audoma_action(
            detail=False,
            methods=["get"],
            results="Car is available"
        )
        def active(self, request, pk=None):
            instance = self.get_object(pk=pk)
            if instnace.active:
                return None, 200
            return "Car is unavailable", 200

Params
^^^^^^^

collectors
""""""""""""
| This param allows defining serializer class which will collect and process request data.
| To define this, action must serve POST/PATCH or PUT method, otherwise
| defining those will cause an exception.
| Collectors may be passed as:


    * Serializer class which must inherit from `serializers.BaseSerializer`

        .. code :: python

            @audoma_action(
                detail=False,
                methods=["post"],
                results=ExampleOneFieldSerializer,
                collectors=ExampleOneFieldSerializer,
            )

    * As dictionary with http methods as keys and serializer classes as values.

        This allows to define different collector for each http method.

        .. code :: python

            @audoma_action(
                detail=True,
                methods=["post"],
                collectors={"post": ExampleModelCreateSerializer},
                results=ExampleModelSerializer,
            )


.. note::

    | Passing collectors is optional, so you don't have to pass them.
    | If collectors won't be passed, and request method will be in `[PUT, POST, PATCH]`
    | then by default, `audoma_action` fill fallback to default
    | `get_serializer_class` method for audoma.

.. note::

    | If you are using collectors it is important to remember,
    | that your action method should accept additional kwarg `collect_serializer`
    | which will be validated collector instance.

results
"""""""""
| This param allows defining custom results for each method and each response status code.
| Results param may be passed as:

    * Serializer class or which must inherit from `serializers.BaseSerializer` or string variable

        In this case the serializer class passed will be used to produce every response
        coming from this action.

        .. code :: python

            @audoma_action(
                detail=True,
                methods=["put", "patch"],
                collectors=ExampleModelCreateSerializer,
                results=ExampleModelSerializer,
            )

    * As dictionary with http methods as keys and serializer classes ot string variables as values.

        In This case, there will be different response serializer for each http method.

        .. code :: python

            @audoma_action(
                detail=False,
                methods=["get", "post"],
                collectors={"post": MyCreateSerializer},
                results={"post": MySerializer, "get": MyListSerializer}
            )


    * As dictionary with http methods as keys and dictionaries as values.
        Those dictionaries has status codes as keys and serializer classes or string variables
        as values.

        .. code-block :: python

            @audoma_action(
                detail=False,
                methods=["post"],
                collectors={"post": MyCreateSerializer},
                results={"post": {201: MySerializer, 204: MyNoContentSerializer}}
            )


.. note::

    | Results param is not mandatory, if you won't pass the results
    | param into audoma_action, then there will be a fallback to default
    | :ref:`get_serializer_class`.

errors
""""""""
| This param is a list of classes and instances of exceptions,
| which are allowed to rise in this action.
| Such behavior prevents rising, not defined exceptions, and allows to document
| exceptions properly in OpenApi schema.

| The main difference between passing exception class and exception instance, is that
| if you pass exception instance, audoma will not only check if exception
| type matches, it'll also validate its content.
| We presume that if you pass, the exception class, you want to accept all exceptions of this class.

| In case the risen exception is not defined in audoma_action errors, there will be another
| exception risen: AudomaActionException, in case the settings.DEBUG = False, this exception
| will be handled silently by logging it, but the code will pass.
| In the case of `settings.DEBUG = True`, then the exception won't be silent.

| By default audoma accepts some exceptions, which are defined globally.
| Those exceptions are:

    * NotFound
    * NotAuthenticated
    * AuthenticationFailed
    * ParseError
    * PermissionDenied


| If you want to extend this list of globally accepted exceptions, you can do it by
| defining `COMMON_API_ERRORS` in your settings, for example:

.. code :: python

    COMMON_API_ERRORS = [
        myexceptions.SomeException
    ]

.. note::

    | Errors param is optional, but if they won't be passed, action will only
    | allow rising globally defined exceptions.

ignore_view_collectors
""""""""""""""""""""""
| Boolean variable which tells if audoma_action should fallback to
| default way of retrieving collector from view, if the collector has not been passed
| and action use method which allows collecting serializer usage.

many
"""""
| This param decides if the returned instance should be treated as many by serializer
| Currently it can only be set to whole action, it is impossible to return instnace and
| multiple instance from one action method using `audoma_action`.


Examples
========

Define example for field
--------------------------

| Above we described :ref:`@extend_schema_field` decorator which allows defining example for field.
| For all fields defined in audoma, there are being examples generated automatically,
| but you may also pass your example as a field parameter.

| Example:

.. code :: python

    from audom.drf import serializers

    class SalesContactSerializer(serializers.Serializer):
        phone_number = serializers.PhoneNumberField(example="+48 123 456 789")
        name = serializers.CharField(example="John", max_length=255)


| After passing the example, it'll be the value shown in example requests in docs.


Define custom fields with auto-generated examples
----------------------------------------------------

| If you want to define your field with auto example generation,
| it is possible, that your field class should inherit from the base `ExampleMixin` class,
| set proper example class.

.. code :: python

    from rest_framework import fields
    from audoma.mixins import ExampleMixin
    from audoma.examples import NumericExample,


    class SaleAmountField(ExampleMixin, fields.Field):
        audoma_example_class = NumericExample


Define custom example classes
--------------------------------

| It is possible to define your custom example classes, by default audio has defined
| two specific example classes inside the `audoma.examples` module:

* `NumericExample`
* `RegexExample`

And one general class:
* `Example`

| To define your example class, you should inherit from the `Example` class
| and override the `generate_value` method

.. code :: python

    from audoma.examples import Example

    class SaleExample(Example):
        def generate_value(self):
            return f"{self.amount} $"

Extra Fields
============

Money Field
------------

| Our money field is an extension of the `MoneyField` known from `django_money`.
| This field is defined as one field in the model, but it creates two fields in the database.

| It creates a separate fields
| There is nothing complex in this field usage, simply define it in your model:

.. code :: python

    from audoma.django.db import models

    class SalesmanStats(models.Model):

        salesman = models.ForeignKey("sale.Salesman", on_delete=models.CASCADE)
        earned = models.MoneyField(max_digits=14, decimal_places=2, default_currency="PLN")


PhoneNumberField
----------------

| Audoma provides a `PhoneNumberField` which is an extension of the `django-phonenumber-field`.
| You can use it in your models straight away, just as the original `PhoneNumberField`_,
| and what we added here is an automatically generated example in documentation,
| based on country code.

.. _PhoneNumberField: https://github.com/stefanfoulis/django-phonenumber-field

| Example:

.. code :: python

    from audoma.django.db import models

    class SalesmanStats(models.Model):

        salesman = models.ForeignKey("sale.Salesman", on_delete=models.CASCADE)
        earned = models.MoneyField(max_digits=14, decimal_places=2, default_currency="PLN")
        phone_number = models.PhoneNumberField(region="GB")



Above will result in the following example in the documentation:

.. code :: json

        {
            "salesman": 1,
            "earned": 500,
            "phone_number": "+44 20 7894 5678",
        }


Serializer Field links
========================

| Audoma allows defining links for serializer fields, which values
| are related to other endpoints. This is useful if you want to limit value choices to
| other filtered endpoint lists.

| Such link won't be visible in redoc/swagger frontend.
| It'll be included in OpenApi schema as :ref:`x-choices`.

| Link definition:

.. code :: python
    from audoma.drf import serializers

    from app.models import Car


    class CarModelSerializer(serializers.ModelSerializer):

        choices_options_links = {
            "manufacturer": {
                "viewname": "manufacturer_viewset-list",
                "value_field": "id",
                "display_field": "name",
            }
        }

        manufacturer = serializers.IntegerField()

        class Meta:
            model = Car
            fields = "__all__"

* viewname - the name of a view from which variables should be retrieved
* value_field - field name from which value should be retrieved
* display_field - field name from which display value should be retrieved



Schema Extensions
==================

x-choices
----------


| This extension is being added to all fields which have limited choice to some range.
| All fields which have defined choices as enum will have this included in their schema.
| If the filter field is also limited to choices this also will be included.

| x-choices may have two different forms.
| The first one when it's just a representation of choices enum.
| Then it'll be a mapping:

.. code :: json

    {
        "x-choices": {
            "choices": {
                "value1": "displayValue1",
                "value2": "displayValue2",
                "value3": "displayValue3",
                "value4": "displayValue4",
            }
        }
    }

| This is simplay a mapping of values to display values.
| This may be useful during displaying choices in for example drop-down.

| The second form of x-choices is:

.. code :: json

    {
        "x-choices": {
            "operationRef": "#/paths/manufacturer_viewset~1",
            "value": "$response.body#results/*/id",
            "display": "$response.body#results/*/name"
        }
    }

| This x-choices is a reference to a different endpoint.
| This may be used to read limited choices from the related endpoint.
| * operationRef - is a JSON pointer to ther related endpoint which should be accesible in this chema
| * value - shows which field should be taken as a field value
| * display - shows which field should be taken as field display value (be shown at frontend)
