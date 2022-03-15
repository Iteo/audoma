from rest_framework.permissions import (
    AND,
    OR,
    OperandHolder,
    SingleOperandHolder,
)


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
