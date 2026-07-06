from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet

from .models import User
from .permissions import IsTenantAdminOrPlatformAdmin
from .serializers import CurrentUserSerializer, UserSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = CurrentUserSerializer(request.user).data
        data["request_tenant"] = request.tenant.id if request.tenant else None
        return Response(data)


class UserViewSet(ModelViewSet):
    queryset = User.objects.select_related("tenant", "branch")
    serializer_class = UserSerializer
    permission_classes = [IsTenantAdminOrPlatformAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_platform_admin:
            return queryset
        if user.tenant_id:
            return queryset.filter(tenant_id=user.tenant_id)
        return queryset.none()

    def perform_create(self, serializer):
        tenant = serializer.validated_data.get("tenant")
        branch = serializer.validated_data.get("branch")
        request_user = self.request.user
        if not request_user.is_platform_admin:
            tenant = request_user.tenant
            if branch and branch.tenant_id != tenant.id:
                raise ValidationError({"branch": "Branch must belong to your tenant."})
        if branch and tenant and branch.tenant_id != tenant.id:
            raise ValidationError({"branch": "Branch must belong to the selected tenant."})
        serializer.save(tenant=tenant)

    def perform_update(self, serializer):
        tenant = serializer.validated_data.get("tenant", serializer.instance.tenant)
        branch = serializer.validated_data.get("branch", serializer.instance.branch)
        request_user = self.request.user
        if not request_user.is_platform_admin and tenant.id != request_user.tenant_id:
            raise ValidationError({"tenant": "Cannot move users outside your tenant."})
        if branch and tenant and branch.tenant_id != tenant.id:
            raise ValidationError({"branch": "Branch must belong to the selected tenant."})
        serializer.save(tenant=tenant)
