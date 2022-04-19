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

* `FieldLinkMixin` - mixin class for serializer fields, which allows you to define OpenApi link on this field.
    To use this your field class must inherit from `FieldLinkMixin`.
    All serializer fields defined in audoma inherits from this mixin.
    Example:
    ```python
        class IntegerField(ExampleMixin, FieldLinkMixin, fields.IntegerField):
            ...
    ```
    To use this you simply have to pass dictionary with link config as `audoma_link` keyword argument to field instance.
    Example:
    ```python

        class ExampleForeignKeyModelSerializer(serializers.ModelSerializer):
            id = serializers.IntegerField(
                choices_link={
                    "viewname": "related_model_viewset-detail",
                    "destinations": {"id": "foreign_key"},
                    "view_kwargs": {"pk": "id"},
                }
            )
        ...

        class ExampleDependedModelSerializer(serializers.ModelSerializer):

            foreign_key = serializers.IntegerField(
                choices_link={
                    "viewname": "example_foreign_key_viewset-list",
                    "sources": {"foreign_key": "id"},
                }
            )
        ...
    ```
    **Available Params:**
    *  viewname[required] - name of related endpoint, related endpoint must be created separately, it should contain exact action
    *  sources - dictionary of related fields sources. By default framework assumes,
        that given variable is refering to `$response.body. If you want field to refer to other place, you should pass full refenrence as dict value, more info: https://swagger.io/docs/specification/links/#runtime-expressions
    * destinations - dictionary of related fields destinations. By default framework assumes,
        that given variable is refering to `$response.body. If you want field to refer to other place, you should pass full refenrence as dict value, more info: https://swagger.io/docs/specification/links/#runtime-expressions
    * view_kwargs - kwargs necessary to retrieve view url, those kwargs will be passed to `reverse` method.
        You should not provide here actual kwargs, only placeholders, Example: `{"foreign_key": "id"}`
    * description - additional description, necesarry if you want to provide additional explonation to link.

    **Note**:
    To allow OpenApi links to work properly your serializer class must inherit from `LinkedSerializerMixin`.
    If your class alread inherits from classes defined in `audoma.serializers`, you don't have to worry about this.
    This funcionality is already provided.

* `LinkedSerializerMixin` - This mixin allows serializer to collect all links from it's fields. Inheriting from this class is
    necessary to make links render properly in docs. During writing custom serializer, you have to inherit from this mixin to provide OpenApi links funcionality. If you inherit from default audoma serializers `audoma.serializers.Serializer` or `audoma.serializers.ModelSerializer` those has this already implemented.

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
