from collections import namedtuple
from typing import List
from typing import Optional

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.inspectors import CoreAPICompatInspector
from drf_yasg.inspectors import NotHandled
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.inspectors.base import call_view_method
from drf_yasg.utils import no_body
from rest_framework.permissions import AND
from rest_framework.permissions import NOT
from rest_framework.permissions import OR
from rest_framework.permissions import OperandHolder
from rest_framework.permissions import SingleOperandHolder


class PermissionDescriptionMixin:
    """View inspector with some project-specific logic."""

    def get_summary_and_description(self):
        """Return summary and description extended with permission docs."""
        summary, description = super().get_summary_and_description()
        permissions_description = self._get_permissions_description()
        if permissions_description:
            description += permissions_description
        return summary, description

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

    def _gather_permissions(self):
        items = {}
        operations = []

        for permission_class in getattr(self.view, 'permission_classes', []):
            if operations:
                operations.append("&")
            items.update(self._handle_permission(permission_class, operations))

        return items, operations

    def _get_permissions_description(self):
        permissions, operations = self._gather_permissions()

        if permissions:
            return '\n\n**Permissions:**\n' + " ".join(operations) + '\n' + '\n'.join(
                self._render_permission_item(name, doc_str) for name, doc_str in permissions.items()
            )
        else:
            return None


class MultiSerializersMixin:
    def get_default_response_serializer(self):
        """Return the default response serializer for this endpoint. This is derived from either the ``request_body``
        override or the request serializer (:meth:`.get_view_serializer`).
        :return: response serializer, :class:`.Schema`, :class:`.SchemaRef`, ``None``
        """
        body_override = self._get_request_body_override()
        if body_override and body_override is not no_body:
            return body_override

        return self.get_view_result_serializer()

    def get_view_result_serializer(self):
        return call_view_method(self.view, 'get_result_serializer')


class DjangoFilterDescriptionInspector(CoreAPICompatInspector):
    def get_filter_parameters(self, filter_backend):
        if isinstance(filter_backend, DjangoFilterBackend):
            result = super().get_filter_parameters(filter_backend)
            # import ipdb;ipdb.set_trace()
            for param in result:
                if not param.get('description', ''):
                    param.description = "Filter the returned list by {field_name}".format(field_name=param.name)
            return result
        return NotHandled


class V2SwaggerAutoSchema(MultiSerializersMixin, PermissionDescriptionMixin, SwaggerAutoSchema):
    pass
