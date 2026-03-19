"""
📚 VIEWS — Reciben requests HTTP, delegan al service, devuelven responses.

Estas views son "thin" (delgadas): no tienen lógica de negocio.
Solo hacen:
1. Recibir el request
2. Validar los datos con un serializer
3. Llamar al service para hacer el trabajo
4. Devolver la response

📚 CLASES USADAS:
- APIView: la view más básica de DRF. Defines métodos como get(), post(), patch().
- Response: crea una response JSON automáticamente.
- status: constantes como HTTP_201_CREATED, HTTP_200_OK, etc.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ChangePasswordSerializer, RegisterSerializer, UserSerializer
from .services import UserService


class RegisterView(APIView):
    """
    POST /api/auth/register/

    📚 permission_classes = [AllowAny]
    Por defecto, en base.py configuramos que TODOS los endpoints requieren autenticación.
    Pero registro es la excepción — cualquiera puede crear una cuenta.
    AllowAny sobreescribe el default solo para esta view.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        📚 Flujo de un POST de registro:
        1. RegisterSerializer valida los datos (email único, passwords coinciden, etc.)
        2. serializer.save() llama a RegisterSerializer.create() que usa create_user()
        3. Devolvemos los datos del usuario creado (sin contraseña, gracias a write_only)
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 📚 raise_exception=True: si la validación falla, DRF automáticamente
        # devuelve un 400 con los errores. No necesitas hacer if/else manual.
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class ProfileView(APIView):
    """
    GET  /api/auth/me/ → ver mi perfil
    PATCH /api/auth/me/ → actualizar mi perfil

    📚 IsAuthenticated es el default (lo configuramos en base.py),
    pero lo ponemos explícito para que quede claro.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        📚 request.user contiene el usuario autenticado (extraído del JWT token).
        SimpleJWT decodifica el token del header "Authorization: Bearer <token>"
        y pone el usuario en request.user automáticamente.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """
        📚 PATCH vs PUT:
        - PATCH: actualización parcial (solo envías los campos que quieres cambiar)
        - PUT: actualización completa (debes enviar TODOS los campos)

        partial=True le dice al serializer "no te quejes si faltan campos".
        """
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        UserService.update_profile(request.user, serializer.validated_data)
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    """
    POST /api/auth/change-password/

    📚 Cambiar contraseña es un endpoint sensible:
    1. Verificamos la contraseña actual (para que si alguien roba tu token, no pueda cambiar la pass)
    2. Hasheamos la nueva contraseña con set_password()
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},  # 📚 Pasamos el request al serializer para acceder a request.user
        )
        serializer.is_valid(raise_exception=True)
        UserService.change_password(request.user, serializer.validated_data["new_password"])
        return Response({"detail": "Contraseña actualizada correctamente."})
