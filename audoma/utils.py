from rest_framework.permissions import AND
from rest_framework.permissions import OR
from rest_framework.permissions import OperandHolder
from rest_framework.permissions import SingleOperandHolder


class PermissionsDescriptionCreator:
    
    def __init__(self, view) -> None:
        self.view = view

    def get_permissions_description(self) -> str:
        permissions, operations = self._gather_permissions()
        if permissions:
            return '\n\n**Permissions:**\n' + " ".join(operations) + '\n' + '\n'.join(
                self._render_permission_item(name, doc_str) for name, doc_str in permissions.items()
            )
        else:
            return ""

    def _gather_permissions(self):
        items = {}
        operations = []

        for permission_class in getattr(self.view, 'permission_classes', []):
            if operations:
                operations.append("&")
            items.update(self._handle_permission(permission_class, operations))

        return items, operations

    def _handle_permission(self, permission_class, operations, current_operation=AND):
        permissions = {}

        if isinstance(permission_class, OperandHolder):
            if permission_class.operator_class == OR and current_operation != OR:
                operations.append("(")
            permissions.update(
                self._handle_permission(permission_class.op1_class, operations, permission_class.operator_class))
            if permission_class.operator_class == OR:
                operations.append("|")
            elif permission_class.operator_class == AND:
                operations.append(" & ")
            permissions.update(
                self._handle_permission(permission_class.op2_class, operations, permission_class.operator_class))
            if permission_class.operator_class == OR and current_operation != OR:
                operations.append(" )")
        elif isinstance(permission_class, SingleOperandHolder):
            permissions.update(
                self._handle_permission(permission_class.op1_class, operations, permission_class.operator_class))

        else:
            try:
                permissions[permission_class.__name__] = permission_class.get_description(self.view),
            except AttributeError:
                if permission_class.__doc__:
                    permissions[permission_class.__name__] = permission_class.__doc__.replace('\n', ' ').strip()
                else:
                    permissions[permission_class.__name__] = "(No description for this permission)"
            operations.append(f"`{permission_class.__name__}`")

        return permissions

    @staticmethod
    def _render_permission_item(name, doc_str):
        return f'+ `{name}`: *{doc_str}*'
