from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CurrentUserSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = CurrentUserSerializer(request.user).data
        data["request_tenant"] = request.tenant.id if request.tenant else None
        return Response(data)
