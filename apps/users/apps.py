"""
📚 AppConfig — Le dice a Django cómo se llama esta app y dónde encontrarla.

Cada app Django tiene un AppConfig. Lo importante aquí es:
- name: la ruta Python completa de la app (apps.users)
- default_auto_field: el tipo de campo para IDs autogenerados
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"          # Ruta completa donde vive la app
    verbose_name = "Usuarios"     # Nombre legible para el admin
