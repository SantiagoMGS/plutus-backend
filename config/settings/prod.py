"""
Settings de PRODUCCIÓN — para cuando se despliegue en un servidor real.

📚 Este es más restrictivo: sin debug, CORS específico, HTTPS forzado.
Por ahora es un placeholder — lo iremos ajustando cuando hagamos deploy.
"""

from .base import *  # noqa: F401,F403

DEBUG = False

# En producción los hosts permitidos deben ser explícitos
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # noqa: F405

# HTTPS — SSL lo maneja el reverse proxy (Traefik/Dokploy)
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
