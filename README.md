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

* `ExampleMixin` allows you to add example documentation value to a serializer field. To use it you just need to inherit
    from `ExampleMixin`, like below and initialize object with example

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

* `audoma_action` decorator - this is a wrapper for standrad drfs' action decorator. It also handles documenting the action. In this decorator this is possible to define:
    * collectors - collect serializers, those are being used to process user input collecotrs may be passed as a serializer class which iherits from serializers.BaseSerializer, it may also be passed as a dict with such structure: {'http_method1': Serializer1, 'http_method2': Serializer2}
    Examples:
    ``` py
    @audoma_action(
        detail=True,
        methods=["post"],
        collectors={"post": ExampleModelCreateSerializer},
        responses={
            "post": {201: ExampleModelSerializer, 202: ExampleOneFieldSerializer}
        },
    )
    def detail_action(self, request, collect_serializer, pk=None):
        ...
    ...
    @audoma_action(
        detail=False,
        methods=["post"],
        responses=ExampleOneFieldSerializer,
        collectors=ExampleOneFieldSerializer,
    )
    def rate_create_action(self, request, collect_serializer):
        ...
    ```
    In case there are no collectors defined audoma_action will try to fallback to standard way of retrieving serializer from view.

    * responses - responses allows to define custom responses for each method, and returned status_code. Responses may be given i three different dictionary forms:
        * {'http_method1': Serializer1Class or string, 'http_method2': Serializer2Class or string}
        * {'http_method1: {status_code: Serializer1Class or string}}
        * {status_code: Serializer1Class or string }
    If the response consist of serializer, it'll simply serialized returned instance, if the response is a string, it'll return it as a message. The response, may be also given simply as a serializer class or a string message.

    Examples:
    ``` py
    @audoma_action(
        detail=True,
        methods=["post"],
        collectors={"post": ExampleModelCreateSerializer},
        responses={
            "post": {201: ExampleModelSerializer, 202: ExampleOneFieldSerializer}
        },
    )
    def detail_action(self, request, collect_serializer, pk=None):
        ...

    @audoma_action(
        detail=False, methods=["get"], responses={"get": "This is a test view"}
    )
    def non_detail_action(self, request):
        ...

    @audoma_action(
        detail=False,
        methods=["post"],
        responses=ExampleOneFieldSerializer,
        collectors=ExampleOneFieldSerializer,
    )
    def rate_create_action(self, request, collect_serializer):
        ...
    ```
    In case there are no responses defined audoma_action will try to fallback to standard way of retrieving
    serializer from view.

    * errors - a list of ApiException subclasses objects. Exceptions defined in this list may be thrown in the action method. Throwing not defined exception will cause throwing ValueError.
    If you are going to raise exception with other message than the one defined in the decorator, decorator will ingore this and still raise exception given in errors list.
    Examples:
    ```py
    @audoma_action(
        detail=False,
        methods=["get"],
        responses=ExampleOneFieldSerializer,
        errors=[CustomBadRequestException(), CustomConflictException()],
    )
    def properly_defined_exception_example(self, request):
        raise CustomConflictException


    @audoma_action(
        detail=False,
        methods=["get"],
        responses=ExampleOneFieldSerializer,
    )
    def improperly_defined_exception_example(self, request):
        raise CustomBadRequestException
    ```
    By default Audoma catch two types of exceptions:
    * NotFound
    * Validation Error
    If you want to add more common exceptions for your API, you should add exception objects in COMMON_API_ERRORS list in your project settings
    Example:
    ```py
        from rest_framework import exceptions
        ...
        COMMON_API_ERRORS = [
            exceptions.NotFound(),
            exceptions.ValidationError(),
        ]
    ```

    While using `audoma_action` custom decorator, your action method should not return the response. To allow `audoma_action` to work properly you should return the instance and the status code as a tuple.
    \
    Examples for serializers:
    * With collect serializer defined
        ```py
        @audoma_action(
            detail=False,
            methods=["post"],
            responses=ExampleOneFieldSerializer,
            collectors=ExampleOneFieldSerializer,
        )
        def rate_create_action(self, request, collect_serializer):
            return collect_serializer.save(), 201
        ```
    * Without collect serializer defined
        ```py
        # TODO
        ```

    Example for string messages:
    ```py
    @audoma_action(
        detail=False, methods=["get"], responses={"get": "This is a test view"}
    )
    def non_detail_action(self, request):
        return None, 200

    ```
    If string defined responses, will return None, it'll simply use the message defined in response, otherwise, it'll return the message passed as an instance

    #### Note:
    You may still use standard `@action` decorator with action methods. It'll still work in Audoma and will take advantage of multiple ViewSet serializers.


* `document_sedocument_serializersrializer` decorator - this decorator is the simple version of audoma_action it's only and main task is to add information about responses, collectors and erros to the decorated function. This allows to access those during generating the schema for OpenAPI. Methods decorated with this decorator does not change it's behaviour, its' only influence documentation.



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
