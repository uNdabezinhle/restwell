from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from .models import Branch, Tenant
from .serializers import BranchSerializer, TenantSerializer


class TenantViewSet(ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAdminUser]


class BranchViewSet(ModelViewSet):
    queryset = Branch.objects.select_related("tenant")
    serializer_class = BranchSerializer
    permission_classes = [IsAdminUser]
