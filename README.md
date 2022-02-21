### audoma - API Automatic Documentation Maker

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
