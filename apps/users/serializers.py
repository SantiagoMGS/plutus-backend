"""
📚 SERIALIZERS — Traducen entre JSON (API) y objetos Python (Django models).

Aquí definimos 3 serializers:
1. RegisterSerializer — valida los datos de registro (username, email, password)
2. UserSerializer — muestra/edita el perfil del usuario (sin contraseña)
3. ChangePasswordSerializer — para cambiar contraseña de forma segura

📚 CONCEPTO CLAVE: "write_only" y "read_only"
- write_only: el campo se ACEPTA en el request pero NUNCA se incluye en la response
  (perfecto para contraseñas — el frontend envía la contraseña, pero nunca la recibe de vuelta)
- read_only: el campo se MUESTRA en la response pero NO se acepta en el request
  (perfecto para campos autogenerados como id, date_joined)
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

# 📚 get_user_model() devuelve el modelo de usuario configurado en AUTH_USER_MODEL.
# Es mejor que importar User directamente porque si cambias el modelo, este código sigue funcionando.
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    📚 Serializer para REGISTRAR un nuevo usuario.

    ModelSerializer genera campos automáticamente a partir del modelo User.
    Nosotros solo especificamos:
    - Qué campos incluir (fields)
    - Configuraciones extra (extra_kwargs)
    - Validaciones custom (validate_*)
    """

    # 📚 Definimos password explícitamente para agregar write_only y min_length.
    # write_only=True → la contraseña se acepta en POST pero NUNCA aparece en la response.
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},  # Para el formulario browsable de DRF
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password_confirm", "currency_default")
        # 📚 extra_kwargs permite agregar configuración a campos sin redefinirlos
        extra_kwargs = {
            "email": {"required": True},  # Django lo hace opcional por defecto — lo forzamos
        }

    def validate_email(self, value):
        """
        📚 validate_<field_name> — DRF llama automáticamente a este método
        cuando valida el campo "email". Si algo está mal, lanzamos ValidationError.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value.lower()  # Normalizamos a minúsculas

    def validate(self, attrs):
        """
        📚 validate() se llama DESPUÉS de validate_<field> individuales.
        Aquí podemos validar campos que dependen entre sí (como password y password_confirm).
        """
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        """
        📚 create() se llama cuando haces serializer.save().
        Aquí usamos create_user() en vez de create() porque:
        - create_user() HASHEA la contraseña (nunca guardar contraseñas en texto plano)
        - create() guardaría la contraseña tal cual → INSEGURO
        """
        validated_data.pop("password_confirm")  # No es un campo del modelo, lo quitamos
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """
    📚 Serializer para VER y EDITAR el perfil del usuario.

    Se usa en:
    - GET /api/auth/me/ → muestra el perfil (serialización)
    - PATCH /api/auth/me/ → actualiza el perfil (deserialización)
    """

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "currency_default", "date_joined")
        # 📚 read_only_fields: estos campos se muestran pero NO se pueden cambiar via API
        read_only_fields = ("id", "username", "email", "date_joined")


class ChangePasswordSerializer(serializers.Serializer):
    """
    📚 Serializer para CAMBIAR la contraseña.

    Este NO es un ModelSerializer — no está atado a un modelo.
    Es un Serializer "puro" donde definimos cada campo manualmente.
    Lo usamos porque cambiar contraseña no es simplemente "actualizar un campo",
    requiere verificar la contraseña actual primero.
    """

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        """Verifica que la contraseña actual sea correcta."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value
