from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DocumentMetadataSerializer, UserSerializer
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

    def delete(self, request):
        UserService.delete_account(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DocumentMetadataView(APIView):
    """
    POST /api/auth/metadata/ → guardar tipo y número de documento en Auth0 user_metadata.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DocumentMetadataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        UserService.save_document_metadata(
            request.user,
            serializer.validated_data["document_type"],
            serializer.validated_data["document_number"],
        )
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
