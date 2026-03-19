"""
Settings de DESARROLLO — solo para tu máquina local.

📚 CONCEPTO: Este archivo importa TODO de base.py y luego sobreescribe
lo que necesita ser diferente en desarrollo.
"""

from .base import *  # noqa: F401,F403 — importa TODAS las settings de base

# ──────────────────────────────────────────────
# DEBUG
# ──────────────────────────────────────────────
DEBUG = True

# ──────────────────────────────────────────────
# HOSTS
# ──────────────────────────────────────────────
ALLOWED_HOSTS = ["*"]  # En dev permitimos todo. En prod NUNCA hagas esto.

# ──────────────────────────────────────────────
# CORS — en desarrollo permitimos todo para no pelear con el frontend
# ──────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ──────────────────────────────────────────────
# EMAIL — en dev los emails se imprimen en la consola en vez de enviarse
# ──────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
