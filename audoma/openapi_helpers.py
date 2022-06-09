from copy import deepcopy
from inspect import isclass
from typing import (
    Callable,
    Type,
    Union,
)

from drf_spectacular.utils import OpenApiResponse
from rest_framework.permissions import (
    AND,
    OR,
    BasePermission,
    OperandHolder,
    SingleOperandHolder,
)
from rest_framework.serializers import BaseSerializer
from rest_framework.views import View


def get_permissions_description(view) -> str:  # noqa: C901
    """
    This is a helper function which generates a description of the permissions.
    Args:
        view - view object

    Returns:
        string with permissions description
    """

    def _render_permission_item(name: str, doc_str: str) -> str:
        return f"+ `{name}`: *{doc_str}*"

    def _handle_permission(
        permission_class: Union[OperandHolder, SingleOperandHolder, BasePermission],
        operations: list,
        current_operation: Type = AND,
    ) -> dict:
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

    def _gather_permissions() -> str:
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


class AudomaApiResponseCreator:
    def extract_collectors(self, view: View) -> dict:
        """
        Simply extracts collectors assigned to the view action method.
        Args:
            view - view instance
        Returns:
            dict of collectors
        """
        action_function = self._extract_action(view)
        _audoma = getattr(action_function, "_audoma", None)
        collectors = getattr(_audoma, "collectors", None)
        return self._parse_action_serializers(collectors)

    def extract_results(self, view: View) -> dict:
        """
        Simply extracts results assigned to the view action method.
        Args:
            view - view instance
        Returns:
            dict of results
        """
        action_function = self._extract_action(view)
        _audoma = getattr(action_function, "_audoma", None)
        results = self._parse_action_serializers(getattr(_audoma, "results", None))
        errors = self._parse_action_errors(getattr(_audoma, "errors", []))
        if results:
            results.update(errors)
            return results

        return errors

    def _extract_action(self, view: View) -> Callable:
        """
        Simply extracts action function defined on the apssed view.
        Args:
            view - view instance
        Returns:
            callable which has been defined as an action.
        """

        action = getattr(view, "action", None)
        if not action:
            return

        return getattr(view, action, None)

    def _parse_action_serializers(self, action_serializers: dict) -> dict:
        """
        Helper method which parses action serializers.
        It allows to display non serializer responses correctly.
        Args:
            action_serializers - dictionary of action collectors/responses
        Retruns:
            Dictionary of parsed collectors/responses.
        """
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

    def _parse_action_errors(self, action_errors: dict) -> dict:
        """
        Helper method which parses action serializers.
        It allows to display non serializer responses correctly.
        Args:
            action_serializers - dictionary of action collectors/responses
        Retruns:
            dictionary of parsed collectors/responses
        """
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
