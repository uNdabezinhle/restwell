from rest_framework.permissions import BasePermission


class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_platform_admin)


class IsTenantAdminOrPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_platform_admin or request.user.role == request.user.Role.TENANT_ADMIN


class IsTenantOperationsUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_platform_admin or request.user.role in {
            request.user.Role.TENANT_ADMIN,
            request.user.Role.STAFF,
            request.user.Role.UNDERWRITER,
        }
