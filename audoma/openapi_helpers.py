from copy import deepcopy
from typing import List

from drf_spectacular.utils import OpenApiExample
from rest_framework.serializers import BaseSerializer


def build_exclusive_fields_schema(
    schema: dict, exclusive_fields: List[str]
) -> List[dict]:
    modified_schemas = []
    for field in exclusive_fields:
        new_schema = deepcopy(schema)
        new_schema["properties"].pop(field)
        modified_schemas.append(new_schema)
    return modified_schemas


def build_exclusive_fields_examples(
    serializer: BaseSerializer,
    exclusive_fields: List[str],
    current_examples: List[OpenApiExample],
) -> List[OpenApiExample]:
    # first generate fields with values
    fields_with_examples = {}
    for field_name, field in serializer.fields.items():
        if hasattr(field, "audoma_example"):
            example = field.audoma_example.example
        else:
            example = type(field_name).__name__
        fields_with_examples[field_name] = example

    # generate few options
    serializer_examples = []
    for x, field in enumerate(exclusive_fields):
        example_values = deepcopy(fields_with_examples)
        example_values.pop(field, None)
        serializer_example = OpenApiExample(
            value=example_values, name=f"Option {x + len(current_examples)}"
        )
        serializer_examples.append(serializer_example)
    return serializer_examples
