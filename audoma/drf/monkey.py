from audoma.drf import serializers
from drf_yasg.inspectors.field import FieldInspector
from drf_yasg.inspectors.field import SerializerInspector
from drf_yasg.inspectors.field import model_field_to_basic_type
from drf_yasg import openapi
from drf_yasg.inspectors.field import serializer_field_to_basic_type
from audoma.django_modelfields import PhoneNumberField
from drf_yasg.inspectors.field import basic_type_info

def add_manual_fields(self, serializer_or_field, schema):
    meta = getattr(serializer_or_field, 'Meta', None)
    swagger_schema_fields = getattr(meta, 'swagger_schema_fields', {})
    if swagger_schema_fields:
        for attr, val in swagger_schema_fields.items():
            if isinstance(val, dict) and isinstance(getattr(schema, attr, None), dict):
                to_update = dict(list(getattr(schema, attr).items()) + list(val.items()))
                setattr(schema, attr, to_update)
            else:
                setattr(schema, attr, val)


FieldInspector.add_manual_fields = add_manual_fields
# SerializerInspector.add_manual_fields = add_manual_fields

basic_type_info += [
    (serializers.PhoneNumberField, (openapi.TYPE_STRING, "tel"))
]
