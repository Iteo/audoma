from drf_spectacular.utils import extend_schema_field

from audoma.drf.fields import FloatField


@extend_schema_field(field={"example": 10.00})
class CustomExampleFloatField(FloatField):
    ...
