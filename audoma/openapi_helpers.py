from copy import deepcopy
from inspect import isclass
from typing import List

from drf_spectacular.drainage import (
    get_override,
    has_override,
)
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
)
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


class AudomaApiResponseCreator:
    def extract_collectors(self, view):
        action_function = self._extract_action(view)
        _audoma = getattr(action_function, "_audoma", None)
        collectors = getattr(_audoma, "collectors", None)
        return self._parse_action_serializers(collectors)

    def extract_results(self, view):
        action_function = self._extract_action(view)
        _audoma = getattr(action_function, "_audoma", None)
        results = self._parse_action_serializers(getattr(_audoma, "results", None))
        errors = self._parse_action_errors(getattr(_audoma, "errors", []))
        if results:
            results.update(errors)
            return results

        return errors

    def _extract_action(self, view):
        action = getattr(view, "action", None)
        if not action:
            return

        return getattr(view, action, None)

    def _parse_action_serializers(self, action_serializers):
        if not action_serializers:
            return action_serializers

        if isinstance(action_serializers, str):
            return {"default": OpenApiResponse(description=action_serializers)}

        if not isinstance(action_serializers, dict):
            return {"default": action_serializers}

        parsed_action_serializers = deepcopy(action_serializers)

        for method, method_serializers in action_serializers.items():
            if isinstance(method_serializers, str):
                parsed_action_serializers[method] = OpenApiResponse(
                    description=method_serializers
                )
            elif isinstance(method_serializers, dict):
                for code, item in method_serializers.items():
                    if isinstance(item, str):
                        parsed_action_serializers[method][code] = OpenApiResponse(
                            description=item
                        )

        return parsed_action_serializers

    def _parse_action_errors(self, action_errors):
        if not action_errors:
            return action_errors

        parsed_errors = {}
        for error in action_errors:
            if isclass(error):
                error = error()

            # build properties
            properties = {}
            for key, value in error.__dict__.items():
                properties[key] = ({key: {"type": type(value).__name__}},)

            parsed_errors[error.status_code] = OpenApiResponse(
                response={
                    "type": "object",
                    "properties": properties,
                    "example": error.__dict__,
                }
            )
        return parsed_errors
