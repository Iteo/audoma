======
Usage
======

.. _get_serializer_class:

Viewset defined serializers
============================

| By default Django Rest Framework provides two methods to get serializer:
| `get_serializer` and `get_serializer_class`.
| Those methods checks if `self` has the property called `serializer_class`
| and returns it or its instance.

| Audoma extends this behaviour, first of all it is possible to
| define `collect` and `result` serializer for given viewset, for all actions.

| Example:

.. code :: python

    class MyViewSet(viewsets.ModelViewSet):
        serializer_class = MySerializer
        collect_serializer_class = MyCollectSerializer
        result_serializer_class = MyResultSerializer

| It is also possible to define custom serializer for each action in the viewset.

| Example:

.. code :: python

    class MyViewSet(viewsets.ModelViewSet):
        create_serializer_class = MyCreateSerializer

| In some specific cases we may want our action to serve more than one http method.
| In audoma it is possible to define serializer per action and method.

| Example:

.. code :: python

    class MyViewSet(viewsets.ModelViewSet):
        get_list_serializer_class = MyListSerializer
        post_list_serializer_class = MyBulkCreateSerializer


| Each action also may want to use different collect
| and result serializers, it is also possible to define this on viewset.

.. code :: python

    class MyViewSet(viewsets.ModelViewSet):
        create_collect_serializer = MyModelCreateSerializer
        create_result_serializer = MyModelSerializer

| In audoma it is also possible to combine all those three variables determining serializer_class usage.
| You may want to have differetn collect/result serializers for action which server mutliple http methods.

| Example:

.. code :: python

    class MyViewSet(viewsets.ModelViewSet):
        get_list_serializer_class = MyListSerializer
        post_list_serializer_class = MyBulkCreateSerializer

| All of above may be defined in one Viewset:

.. code :: python

        class MyViewSet(viewsets.ModelViewSet):
            serializer_class = MySerializer
            collect_serializer_class = MyCollectSerializer
            result_serializer_class = MyResultSerializer
            create_serializer_class = MyCreateSerializer
            get_list_serializer_class = MyListSerializer
            post_list_serializer_class = MyBulkCreateSerializer

| In case there are multiple name conventions used, serializer will be discovered in following order:

* `{method}_{action}_{type}_serializer_class`
* `{action}_{type}_serializer_class`
* `{method}_{action}_serializer_class`
* `{action}_serializer_class`
* `common_{type}_serializer_class`
* `serializer_class`

| What's important all of the serializers defined this way, will be documented properly.

Permissions
===========

By default in `drf-spectacular` viewset permissions were not documented at all.
Currently permissions are being documented for each viewset separately.

You don't have to define anything extra, this is being handled just out of the box.
The only thing it is required is to define permissions on your viewset.

Example:

.. code :: python

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
        ...

.. _choices:

Custom choices
==============
| Audoma provides convenient method of creting choices.
| This method allows to reffer to choices by it's name.

Example:
.. code :: python

    if body_type == BODY_TYPE_CHOICES.SEDAN:
        ...

To create custom choices you have to use `make_choices` method.

.. code :: python

    from audoma.choices import make_choices
    ...

    class ExampleModel(models.Model):

        EXAMPLE_CHOICES = make_choices(
            "CHOICES",
            (
                (1, "EX_1", "example 1"),
                (2, "EX_2", "example 2"),
                (3, "EX_3", "example 3"),
            ),
        )

        ....
    choices = models.IntegerField(choices=EXAMPLE_CHOICES.get_choices())

| As you may see if you are passing those choice into a model field you should use `get_choices` method.
| This will return the choices in known from django.

| If you use this choices with :ref:`DocumentedTypedChoiceFilter` , there will be internal values available in API.
| Otherwise this will be displayed as default choices, so in API, as value there will be the databse value.



Filters
=======

Default Filters
----------------

| In drf it's possible to define `filterset_fields` and `filterset_class`.
| By default drf-spectacular supports django-filters. Which are being documented.
| Audoma has been tested with default drf's filter backend and `DjangoFilterBackend`.
| For more accurate documentation we recommend to use `DjangoFilterBackend` as default one.
| Filters and search fields are being documented out of the box automatically:

.. code :: python

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


| It is also possible to define filterset class which will also be documented
| without any additional steps.

| The main extension of this feature in audoma is additional enum documentation.
| In `drf-spectacular` enums are being shown only as values possible to pass to the filter.
| Using audoma you also get a display field of a choice, this may be useful to show display value
| in a drop-down for example.

| Additionaly enum fields get extension value in OpenApi schema, which is not
| visible in redoc/swagger frontend. This value is :ref:`x-choices`, you may read about it here.


DocumentedTypedChoiceFilter
---------------------------

| This is an extension for `TypedChoiceFilter` from `django-filters`.
| This extends filter field help text, it changes the way of rendering enums.
| It takes advatage of audoma :ref:`choices` solution.

| In case of using `DocumentedTypedChoiceFilter` there will be three values for `choices`.
| Two of those values will be api values, and the third value will be the database value.
| Api values are display value, and the internal api value, which won't used on databse, this will be
| mapped to the third value, which is being used inside database.

| This field also create x-choices entry in OpenApi schema.


Validators
===========

ExclusiveFieldsValidator
--------------------------

| This is an additional validator, which allows to define mutually exclusive fields in serializer.
| It validates if any of fields has been given, and if not all exclusive fields has been given.

| This validator takes params:

* fields - list or a tuple of field names
* message - string message, which will replace defaul validator message
* required - boolean which determines if any of field must be given
* message_required - message which will be displayed if one of fields was required,
    and none has been passed

| Usage is quite simple:

.. code :: python

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
--------------------

| This decorator is a basic drf-spectacular decorator, but it's behavior has been changed.
| It allows to pass example to the field without using information about the field.
| Data is not overriden, it's updated.

.. code :: python

    from audoma.drf.fields import FloatField

    from drf_spectacular.utils import extend_schema_field

    @extend_schema_field(
        field={
            "example": 10.00
        }
    )
    class CustomExampleFloatField(FloatField):
        ...

| This decorator also allows to pass all used by drf-spectacular parameters.

@audoma_action
---------------
| This is one of the most complex features offered by audoma.
| In fact this is an extension of action decorator, which by default is Django Rest Framewok functionality.
| It also allows to register custom action for viewset.
| In case of audoma_action it is also possible to define additional parmeters, such as:

collectors
""""""""""
| This param allows to define serializer class which will collect and process request data.
| To define this, action must serve POST/PATCH or PUT method.
| Collectors may be define in few ways:

.. code :: python

    @audoma_action(
        detail=False,
        methods=["post"],
        results=ExampleOneFieldSerializer,
        collectors=ExampleOneFieldSerializer,
    )

| As defined above, simply as a serializer class, which must inherit from `serializers.BaseSerializer`.

.. code :: python

    @audoma_action(
        detail=True,
        methods=["post"],
        collectors={"post": ExampleModelCreateSerializer},
        results={
            "post": {201: ExampleModelSerializer, 202: ExampleOneFieldSerializer}
        },
    )
    def detail_action(self, reqDocumentedTypedChoiceFilteruest, collect_serializer, pk=None):
        ...

| It also may be defined as a dictionary with given http methods, than
| the collectors, will be used for each http method. For Example, we may define
| different collectors for post an patch.

.. code :: python

    @audoma_action(
        detail=True,
        methods=["post", "patch"],
        collectors={
            "post": ExampleModelCreateSerializer,
             "patch": ExampleModelUpdateSerializer
        },
        results={
            "post": {
                201: ExampleModelSerializer,
                202: ExampleOneFieldSerializer
            },
            "patch": {
                200: ExampleModelSerializer,
                202: ExampleOneFieldSerializer
            }
        },
    )
    def detail_action(self, request, collect_serializer, pk=None):
        ...

| This parameter is optional, so you don't have to pass collectors. If collectors won't be passed, and
| request method will be in `[PUT, POST, PATCH]` than by default, audoma_action fill fallback to default
| `get_serializer_class` method for audoma.

**Important**

| If you are using collectors it is important to remember,
| that your method should tak additional kwarg `collect_serializer` which will be
| validated collector instance.

results
"""""""
| This param allows to define custom results for each method and each response status code.
| Results may be defined in three possible forms:

.. code :: python

    @audoma_action(
        detail=True,
        methods=["put", "patch"],
        collectors=ExampleModelCreateSerializer,
        results=ExampleModelSerializer,
    )
    def example_update_action(self, request, collect_serializer, pk=None):
        ...

| As a serializer class, which must inherit from the `serializers.BaseSerializer`.
| This will be used to serializer, returned instance

.. code :: python

    @audoma_action(
        detail=True,
        methods=["post"],
        collectors={"post": ExampleModelCreateSerializer},
        results={"post": {201: ExampleModelSerializer, 202: ExampleOneFieldSerializer}},
    )
    def detail_action(self, request, collect_serializer, pk=None):
        ...

    @audoma_action(
        detail=False,
        methods=["get"],
        results={"get": {200: "This is a test view", 404: "Not found"}},
    )
    def non_detail_action(self, request):
        ...


| As a dictionary with http methods and status code, where dict values, may be serializer
| classes or text messages. If values will be serializers,
| view should return alongside status code, an instnace which may be serialized.
| If those are messages, view should return None as an instance,
| or an overriding message for given status code.

| Results are not mandatorty parameter, if you won't pass results
| param into audoma_action, than there will be a fallback to default
| :ref:`get_serializer_class`.

errors
""""""""
| This param may be a list of classes and instances of exceptions, which are
| allowed to be risen in this action. Such behaviour prevents rising, not defined exceptions, and allows
| to document such exceptions properly in OpenApi schema.

| The main difference between passing exception class and exception instance, is that
| if you pass exception instance, audoma will not only check if exception
| type matches, it'll also validate it's content.
| We presume that if you pass, the exception class, you want to accept all exceptions of this class.

| In case the risen exception is not defined in audoma_action errors, there will be another
| exception risen: AudomaActionException, in case the settings.DEBUG = False, this exception
| will be handled silently by logging it, but the code will pass. In case of settings.DEBUG = True,
| than the exception won't be silent.

| By default audoma accepts some exceptions, which are defined globally.
| Those exceptions are:

* NotFound
* NotAuthenticated
* AuthenticationFailed
* ParseError
* PermissionDenied


| If you want to extend this list of globally accepted exceptions, you can do it by
| defining `COMMON_API_ERRORS` in your settings, example:

.. code :: python

    COMMON_API_ERRORS = [
        myexceptions.SomeException
    ]

ignore_view_collectors
""""""""""""""""""""""
| Boolean variable which tells if audoma_action should fallback to
| default way of retrieving collector from view, if collector has not been passed
| and action uses method which allows collect serializer usage.


Examples
========

Define example for field
--------------------------

| Above we described :ref:`@extend_schema_field` decorator which allows to define example for field.
| For all fields defined in audoma, there are being examples generated automatically,
| but you may also pass your own example as field parameter.

| Example:

.. code :: python

    class ExampleSerializer(serializers.Serializer):
        ...
        phone_number_example = serializers.PhoneNumberField(example="+48 123 456 789")
        ...

Define custom fields with auto-generated examples
----------------------------------------------------

| If you want to define your own field with auto example generation,
| it is possible, your field class should inherit from base `ExampleMixin` class,
| set proper example class.

.. code ::python

    from rest_framework import fields
    from audoma.mixins import ExampleMixin
    from audoma.examples import NumericExample,


    class SomeExampleField(ExampleMixin, fields.Field):
        audoma_example_class = NumericExample

Define custom example classes
--------------------------------

| It is possible to define your own custom example classes, by default audoma has defined
| two specific example classes inside `audoma.examples` module:

* `NumericExample`
* `RegexExample`

And one general class:
* `Example`

| To define you own example class, you should inherit from `Example` class
| and override `generate_value` method

.. code :: python

    from audoma.examples import Example

    class MyExample(Example):
        def generate_value(self):
            return "My example value"


Extra Fields
============

Money Field
------------

| Our money field is an extension for money field known from `django_money`.
| This field is defined as one field in model, but it creates two fields in databse.

| It create separate field for amount and currency. This is useful during serialization,
| because in most cases you want to serialize amount and currency separately.

| There is nothing complex in this field usage, simply define it in your model:

.. code :: python

    from audoma.django.db import models

    class ExamplePerson(models.Model):
        ...
        savings = models.MoneyField(max_digits=14, decimal_places=2, default_currency="PLN")
        ...


PhoneNumberField
----------------

# TODO - write docs

Serializer Field links
========================

| Audoma allows to define links for serializer fields, which values
| are related to other endpoints. This is useful if you want to limit value choices to
| other filtered endpoint list.

| Such link won't be visible in redoc/swagger frontend.
| It'll be included in OpenApi schema as :ref:`x-choices`.

| Link definition:

.. code :: python

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

* viewname - name of a view from which variables should be retrieved
* value_field - field name from which value should be retrieved
* display_field - field name from which display value should be retrieved



Schema Extensions
==================

x-choices
----------


| This extension is being added to all fields which have limited choice to some range.
| All fields which have defined choices as enum will have this included in their schema.
| If filter field is also limited to choices this also will be included.

| x-choices may have two different forms.
| The first one when it's just a representation of choices enum.
| Than it'll be a maping:

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

| This x-choices is a reference to diferent endpoint.
| This may be used to read limited choices form related endpoint.
| * operationRef - is a JSON pointer to ther related endpoint which should be accesible in this chema
| * value - shows which field should be taken as field value
| * display - shows which field should be taken as field display value (be shown at frontend)
