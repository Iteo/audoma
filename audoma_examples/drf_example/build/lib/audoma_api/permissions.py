from rest_framework.permissions import BasePermission


class ViewAndDetailPermission(BasePermission):
    """The ViewAndDetailPermission guard access to all views nad detail views (collections and resources).
    General view permission is determined first then if it's detail view specific object permission is checked.
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True


class DetailPermission(BasePermission):
    """The DetailPermission guard access to Detail Views (resources)."""

    def has_object_permission(self, request, view, obj):
        return True


class ViewPermission(BasePermission):
    """The ViewPermission guard access to all views in ViewSet (collections and resources)."""

    def has_permission(self, request, view):
        return True


class AlternatePermission1(BasePermission):
    """The AlternatePermission1 is combined through OR operator with AlternatePermission2"""

    def has_permission(self, request, view):
        return True


class AlternatePermission2(BasePermission):
    """The AlternatePermission2 is combined through OR operator with AlternatePermission1"""

    def has_permission(self, request, view):
        return True


# check_object_permissions
