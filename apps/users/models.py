"""
📚 MODELO USER — El corazón de la autenticación

En Django, todo gira alrededor del User. Cada transacción, cuenta, categoría
está vinculada a un usuario. Por eso definimos nuestro propio modelo.

📚 ¿Qué es AbstractUser?
Django tiene una clase `AbstractUser` que ya incluye todo lo necesario:
- username, email, password (hasheado, nunca en texto plano)
- first_name, last_name
- is_active, is_staff, is_superuser (permisos)
- date_joined, last_login

Nosotros la "extendemos" (herencia) para agregar campos propios.
Es como decir: "Quiero todo lo que ya tiene User, PERO ADEMÁS quiero estos campos extra".
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modelo de usuario personalizado para Plutus.

    📚 HERENCIA: User hereda de AbstractUser.
    Esto significa que User tiene TODOS los campos y métodos de AbstractUser
    (username, email, password, etc.) más los que definamos aquí abajo.
    """

    # ── Campos personalizados ──

    # 📚 models.CharField = campo de texto con longitud máxima fija
    # max_length = máximo de caracteres permitidos
    # default = valor que se asigna si el usuario no especifica uno
    currency_default = models.CharField(
        max_length=3,
        default="COP",
        help_text="Moneda por defecto del usuario (código ISO 4217: USD, EUR, COP, etc.)",
    )

    class Meta:
        # 📚 Meta es una clase interna que configura metadatos del modelo.
        # db_table = nombre de la tabla en la base de datos
        db_table = "users"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        # 📚 __str__ define qué se muestra cuando imprimes un objeto User.
        # Ej: print(user) → "santiago (santiago@email.com)"
        return f"{self.username} ({self.email})"
