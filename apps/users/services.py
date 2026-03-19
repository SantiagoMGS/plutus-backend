"""
📚 SERVICE LAYER — Lógica de negocio de Users.

Este archivo contiene TODA la lógica de negocio relacionada con usuarios.
Las views NO deben tener lógica — solo delegan al service.

📚 ¿Por qué separar esto?
Sin service layer:
    View → hace validación + lógica + guarda en BD (todo mezclado)

Con service layer:
    View → llama a UserService.register_user(data)
    Service → valida, crea el usuario, cualquier lógica extra
    Model → se guarda en BD

Beneficio: si mañana necesitas crear un usuario desde un management command
o desde otra parte del código, llamas a UserService directamente sin depender de HTTP/DRF.
"""

from __future__ import annotations

from .models import User


class UserService:
    """Servicio para operaciones de usuario."""

    @staticmethod
    def register_user(validated_data: dict) -> User:
        """
        📚 Registra un nuevo usuario.

        @staticmethod significa que puedes llamar este método SIN crear una instancia:
            UserService.register_user(data)  ← correcto
        En vez de:
            service = UserService()
            service.register_user(data)      ← innecesario

        Recibe los datos ya validados por el serializer y crea el usuario.
        """
        return User.objects.create_user(**validated_data)

    @staticmethod
    def update_profile(user: User, validated_data: dict) -> User:
        """Actualiza los campos del perfil del usuario."""
        for field, value in validated_data.items():
            setattr(user, field, value)
        user.save(update_fields=validated_data.keys())
        return user

    @staticmethod
    def change_password(user: User, new_password: str) -> None:
        """
        📚 Cambia la contraseña del usuario.

        set_password() hashea la contraseña automáticamente.
        NUNCA hagas user.password = "nueva" — eso guardaría la contraseña en texto plano.
        """
        user.set_password(new_password)
        user.save(update_fields=["password"])
