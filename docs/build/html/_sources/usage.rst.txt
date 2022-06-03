======
Usage
======

Viewset defined serializers
============================

Permissions
===========

Filters
=======

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

| This decorator also allowst to pass all used by drf-spectacular parameters.

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
    def rate_create_action(self, request, collect_serializer):
        ...

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
    def detail_action(self, request, collect_serializer, pk=None):
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
| `get_serializer_class` method used in audoma.

# TODO - add reffernece to get_serializer_class description

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
""""
| If you want to extend this list of globally accepted exceptions, you can do it by
| defining `COMMON_API_ERRORS` in your settings, example:

.. code :: python

    COMMON_API_ERRORS = [
        myexceptions.SomeException
    ]

ignore_view_collectors
""""""""""""""""""""""
Boolean variable which tells if audoma_action should fallback to
default way of retrieving collector from view, if collector has not been passed
and action uses method which allows collect serializer usage.


Examples
========
