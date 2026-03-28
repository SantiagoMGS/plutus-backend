from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer
from .services import UserService


class ProfileView(APIView):
    """
    GET  /api/auth/me/ → ver mi perfil
    PATCH /api/auth/me/ → actualizar mi perfil
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        UserService.update_profile(request.user, serializer.validated_data)
        return Response(UserSerializer(request.user).data)
