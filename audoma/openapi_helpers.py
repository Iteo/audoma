from copy import deepcopy
from typing import List

from drf_spectacular.drainage import (
    get_override,
    has_override,
)
from drf_spectacular.utils import OpenApiExample
from rest_framework.permissions import (
    AND,
    OR,
    OperandHolder,
    SingleOperandHolder,
)
from rest_framework.serializers import BaseSerializer


def get_permissions_description(view):  # noqa: C901
    def _render_permission_item(name, doc_str):
        return f"+ `{name}`: *{doc_str}*"

    def _handle_permission(permission_class, operations, current_operation=AND):
        permissions = {}

        if isinstance(permission_class, OperandHolder):
            if permission_class.operator_class == OR and current_operation != OR:
                operations.append("(")
            permissions.update(
                _handle_permission(
                    permission_class.op1_class,
                    operations,
                    permission_class.operator_class,
                )
            )
            if permission_class.operator_class == OR:
                operations.append("|")
            elif permission_class.operator_class == AND:
                operations.append(" & ")
            permissions.update(
                _handle_permission(
                    permission_class.op2_class,
                    operations,
                    permission_class.operator_class,
                )
            )
            if permission_class.operator_class == OR and current_operation != OR:
                operations.append(" )")
        elif isinstance(permission_class, SingleOperandHolder):
            permissions.update(
                _handle_permission(
                    permission_class.op1_class,
                    operations,
                    permission_class.operator_class,
                )
            )

        else:
            try:
                permissions[permission_class.__name__] = (
                    permission_class.get_description(view),
                )
            except AttributeError:
                if permission_class.__doc__:
                    permissions[
                        permission_class.__name__
                    ] = permission_class.__doc__.replace("\n", " ").strip()
                else:
                    permissions[
                        permission_class.__name__
                    ] = "(No description for this permission)"
            operations.append(f"`{permission_class.__name__}`")

        return permissions

    def _gather_permissions():
        items = {}
        operations = []

        for permission_class in getattr(view, "permission_classes", []):
            if operations:
                operations.append("&")
            items.update(_handle_permission(permission_class, operations))

        return items, operations

    permissions, operations = _gather_permissions()
    if permissions:
        return (
            "\n\n**Permissions:**\n"
            + " ".join(operations)
            + "\n"
            + "\n".join(
                _render_permission_item(name, doc_str)
                for name, doc_str in permissions.items()
            )
        )
    else:
        return ""


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
        if has_override(field, "field"):
            schema = get_override(field, "field")
            example = schema.get("example")
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
