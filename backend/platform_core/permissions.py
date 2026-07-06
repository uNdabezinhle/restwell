from rest_framework.permissions import BasePermission

from .services import feature_enabled


class HasTenantFeature(BasePermission):
    message = "This module is not enabled for the current tenant."

    def has_permission(self, request, view):
        code = getattr(view, "feature_code", None)
        if not code:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_platform_admin:
            return True
        return feature_enabled(getattr(user, "tenant", None), code)
