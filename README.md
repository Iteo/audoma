### audoma - API Automatic Documentation Maker


[![pipeline status](https://gitlab.iteo.com.pl/python/audoma/badges/main/pipeline.svg)](https://gitlab.iteo.com.pl/python/audoma/-/commits/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

The main goal of this project is to make Django Rest Framework documentation easier and more automatic.
It supports drf-spectacular documentation and extends some of its functionalities.

Installation
------------
Install using ``pip``. You will need deployment token to install this repository


```
    $ pip install git+https://gitlab+deploy-token-94:${AUDOMA_DEPLOYMENT_TOKEN}@gitlab.iteo.com.pl/python/audoma.git@main
```

then register AudomaAutoSchema as default schema class in DRF application.

```python
REST_FRAMEWORK = {
    # YOUR SETTINGS
    'DEFAULT_SCHEMA_CLASS': 'audoma.drf.openapi.AudomaAutoSchema',
}
```

Audoma allows you to add path prefixes that should be included in schema exclusively. All you need to do is declare a variable
`SCHEMA_PATTERN_PREFIX` in your `settings.py` file and add preprocessing function `preprocess_include_path_format` as preprocessing
hook in `SPECTACULAR_SETTINGS` dictionary as in the example below.

```python
SCHEMA_PATTERN_PREFIX = 'api'

SPECTACULAR_SETTINGS = {
    ...
    'PREPROCESSING_HOOKS': ['audoma.hooks.preprocess_include_path_format'],
    # OTHER SETTINGS
}
```

Usage
------------
Audoma works with DRF and drf-spectacular, and here are some functionalities added:

* `@extend_schema_field` decorator - you can add example without loosing information about of a field in documentation,
    with AutoSchema from drf-spectacular, you would have to declare type and format, otherwise it would be daclared as any

    ```python
    @extend_schema_field(
        field={
            "example": 10.00
        }
    )
    class FloatField(fields.FloatField):
        pass
    ```

* `ExampleMixin` allows you to add example documentation value to a serializer field. To use it you just need to use fields defined in
    `audoma.drf.fields` or inherit from `ExampleMixin` or use fields defined in `audoma.drf.fields`, like below and initialize object with example

    ```python
    class FloatField(ExampleMixin, fields.FloatField):
        pass


    class ExampleSerializer(serializers.Serializer):
        float_field = serializers.FloatField(example=23.45)
    ```

    Example abow will result in documentation

    ```json
    {
    "float_field": 23.45
    }
    ```

    You can also add example directly to model fields. It works the same way as in serializers, just inherit from `ModelExampleMixin`, or
    use audoma's fields defined in `audoma.django.db` and initialize model field with example like shown below.

    ```python
    from audoma.django.db import models

    class Person(models.Model):
        first_name = models.CharField(max_length=255, example="Tom")
    ```


* `DocumentedTypedChoiceFilter` is a wrapper to `df.filters.TypedChoiceFilter` that makes creating documentation easier. It goes out of the box with
    our `make_choices` function for quickly making a namedtuple suitable for use in a django model as a choices attribute on a field that will preserve order.
    Below you can see an example of usage.

    `models.py`
    ```python
    from audoma.choices import make_choices
    #define a model with use of make_choices
    class MyModel(models.Model):
            COLORS = make_choices('COLORS', (
                (0, 'BLACK', 'Black'),
                (1, 'WHITE', 'White'),
            ))
            colors = models.PositiveIntegerField(choices=COLORS)
            ...

    ```
    `views.py`
    ```python
    #In views define DocumentedTypedChoiceFilter
    example_choice = DocumentedTypedChoiceFilter(
    MyModel.EXAMPLE_CHOICES,
    'color',
    lookup_expr='exact',
    field_name='colors'
    )


    class ExampleChoiceFilter(df_filters.FilterSet):
        choice = example_choice

        class Meta:
            model = ExampleModel
            fields = ['color', ]

    #then, use example_choice to create automatic description with extend_schema
    @extend_schema(parameters=[example_choice.create_openapi_description()])
    class ExampleModelViewSet():
        ...
    ```

* We also support documentation of `MoneyField` from `django-money` package which allows you to handle money and currency values

* `audoma_action` decorator - this is a wrapper for standrad drfs' action decorator. It also handles documenting the action. In this decorator this is possible to pass:
    * **collectors** - collect serializers, those are being used to process users input, collectors may be
     passed as a serializer class which inherits from `serializers.BaseSerializer`, it may also be passed as a dict with given structure: {'http_method1': Serializer1Class, 'http_method2': Serializer2Class}.
    If collectors won't be passed to the audoma_action decorator and request method will allow to use collect serializer, decorator will try to retrieve collect serializer from view.

        **WARNING**  - if passed methods does not allow to define collectors (methods are "safe methods", so they can only read data), there will be ImproperlyConfigured exception raised.
        \
        Examples:
        ``` py
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
        ...
        @audoma_action(
            detail=False,
            methods=["post"],
            results=ExampleOneFieldSerializer,
            collectors=ExampleOneFieldSerializer,
        )
        def rate_create_action(self, request, collect_serializer):
            ...
        ```
        In case there are no collectors defined and http method is not a safe method, then audoma_action will try to fallback to standard way of retrieving collect serializer from view.

        If audoma_action will extract proper collector, it'll be validated and passed into action method as parameter.

    * **results** - allow to define custom results for each method, and returned status_code. results may be given in three different dictionary forms:
        * {'http_method1': Serializer1Class or string, 'http_method2': Serializer2Class or string}
        * {'http_method1: {status_code: Serializer1Class or string}}
        * {status_code: Serializer1Class or string }
    If the response consist of serializers classes, it'll simply serialize returned instance, if the response is a string, it'll return it as a message. The response, may be also given simply as a serializer class or a string message:
        * results="This is a response message"
        * results=Serializer1Class
     \
    Examples:
        ``` py
        @audoma_action(
            detail=True,
            methods=["post"],
            collectors={"post": ExampleModelCreateSerializer},za
            results={
                "post": {201: ExampleModelSerializer, 202: ExampleOneFieldSerializer}
            },
        )
        def detail_action(self, request, collect_serializer, pk=None):
            ...

        @audoma_action(
            detail=False, methods=["get"], results={"get": "This is a test view"}
        )
        def non_detail_action(self, request):
            ...

        @audoma_action(
            detail=False,
            methods=["post"],
            results=ExampleOneFieldSerializer,
            collectors=ExampleOneFieldSerializer,
        )
        def rate_create_action(self, request, collect_serializer):
            ...
        ```
        In case there are no results defined audoma_action will try to fallback to standard way of retrieving serializer from view.


    * **errors** - a list of classes or instances which inherits from base Exception class. Exceptions defined in this list may be thrown in the action method. If you would like to accept all exceptions of given class simply pass exception class to the list, otherwise pass precise exception instance, than the exception content will also be verified. If you passed exception instance, if DEBUG=True, and the raised exception content won't match the exception defined in decorator, this will cause rising AudomaActionException, if DEBUG=False then there'll only appear logger exception, but your exception will be risen. If you'll try to rise exception which is not gently handled by django (for example ValueError), than also if DEBUG=True you'll get AudomaActionException, otherwise, there will appear logger exception, but exception will not be risen.
        \
        Examples:
        ```py
        @audoma_action(
            detail=False,
            methods=["get"],
            results=ExampleOneFieldSerializer,
            errors=[CustomBadRequestException(), CustomConflictException()],
        )
        def properly_defined_exception_example(self, request):
            raise CustomConflictException


        @audoma_action(
            detail=False,
            methods=["get"],
            results=ExampleOneFieldSerializer,
        )
        def improperly_defined_exception_example(self, request):
            raise CustomBadRequestException
        ```
        By default Audoma accepts exceptions:
        * NotFound
        * NotAuthenticated
        * AuthenticationFailed
        * ParseError
        * PermissionDenied
        * NotAcceptable
        * ValidationError
        \
        If you want to add more common exceptions for your API, you should add exception objects or classes in COMMON_API_ERRORS list in your project settings
        Example:
        ```py
            ...
            COMMON_API_ERRORS = [
                myexceptions.SomeException
            ]
        ```

        **NOTE: this is not possible to define exceptions with extra required params as classes.**

    * **ignore_view_collectors** - boolean variable which tells if audoma_action should fallback to default way of retrieving collector from view, if collector has not been passed and action uses method which allows collect serializer usage.
    \
    While using `audoma_action` custom decorator, your action method should not return the response. To allow `audoma_action` to work properly you should return the instance and the status code as a tuple.
    \
    Examples for serializers:
    * With collect serializer defined
        ```py
        @audoma_action(
            detail=False,
            methods=["post"],
            results=ExampleOneFieldSerializer,
            collectors=ExampleOneFieldSerializer,
        )
        def rate_create_action(self, request, collect_serializer):
            return collect_serializer.save(), 201
        ```
    * Without collect serializer defined
        ```py
        @audoma_action(detail=True, methods=["get"], results=ExampleOneFieldSerializer)
        def specific_rate(self, request, pk=None):
            return {"rate": 1}, 200
        ```

    * Example for string messages:
        ```py
        @audoma_action(
            detail=False, methods=["get"], results={"get": "This is a test view"}
        )
        def non_detail_action(self, request):
            return None, 200

        ```
        If string defined results, will return None, it'll simply use the message defined in response, otherwise, it'll return the message passed as an instance

    #### Note:
    You may still use standard `@action` decorator with action methods. It'll still work in Audoma.


Testing and example application
------------
 #### Running example application
You can easily test audoma functionalities with our example applicaiton.
From root folder, go to `docker/` and run `docker-compose up example_app`.
You can explore possibilities of audoma documentation maker as it shows all functionalities.
#### Runing tests
Go to `docker/` and run
`docker-compose run --rm example_app bash -c "cd audoma_examples/drf_example && python manage.py test"`


Development
------------
Project has defined code style and pre-commit hooks for effortless code formatting.

To setup pre-commit hooks inside repo run:
```
    $ pip install -r requirements_dev.txt
    $ pre-commit install
```
From now on your commits will fail if your changes break code conventions of the project.

To format project and apply all code style conventions run:
```
    $ ./autoformat.sh
```
This command can be triggered automatically by IDE on file save or on file change.
