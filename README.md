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


Testing and example application
------------
You can test audoma functionalities with our example applicaiton. From root folder,
go to `audoma_examples/drf_examples` and create virtualenv there. Then, install audoma
and run django application. You can easily explore possibilities of audoma documentation maker
as it shows all functionalities. To run tests simply run `python manage.py test` command.


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
