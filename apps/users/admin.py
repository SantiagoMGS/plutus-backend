"""
📚 ADMIN — Registrar el modelo User en el panel de administración de Django.

Django viene con un panel admin auto-generado (localhost:8000/admin/).
Aquí le decimos: "muestra los usuarios en el panel admin, usando
el formulario especial para usuarios (con campos de contraseña, etc.)"
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    📚 @admin.register(User) = decorador que registra este modelo en el admin.
    BaseUserAdmin ya sabe cómo mostrar un formulario de usuario con contraseña,
    permisos, etc. Solo agregamos nuestro campo 'currency_default'.
    """

    # Agrega currency_default a la sección "Información personal" del formulario
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Preferencias", {"fields": ("currency_default",)}),
    )
