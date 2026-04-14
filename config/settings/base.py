"""
Settings BASE — compartidos entre todos los entornos (dev, prod, staging).

📚 CONCEPTOS CLAVE:
- environ.Env: lee variables de entorno (.env file o del sistema operativo)
- INSTALLED_APPS: lista de "apps" habilitadas. Django solo conoce las apps que listamos aquí.
- MIDDLEWARE: pipeline de procesamiento que cada request/response atraviesa (como capas de cebolla)
- AUTH_USER_MODEL: le dice a Django "usa MI modelo de usuario, no el default"
"""

import environ
from pathlib import Path

# ──────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────
# BASE_DIR apunta a plutus-backend/ (3 niveles arriba de este archivo)
# Este archivo está en: config/settings/base.py
# parent = config/settings/ → parent = config/ → parent = plutus-backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ──────────────────────────────────────────────
# ENVIRONMENT VARIABLES (django-environ)
# ──────────────────────────────────────────────
# Creamos una instancia de Env con valores por defecto.
# Estos defaults son SOLO para desarrollo local. En producción se leen del entorno real.
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)

# Lee el archivo .env si existe (en producción normalmente no existe,
# las variables vienen del sistema operativo o Docker)
environ.Env.read_env(BASE_DIR / ".env")

# ──────────────────────────────────────────────
# SECURITY
# ──────────────────────────────────────────────
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# ──────────────────────────────────────────────
# INSTALLED APPS
# ──────────────────────────────────────────────
# 📚 Django carga estas apps al iniciar. Cada app puede tener: models, views, signals, admin, etc.
# Se dividen en 3 grupos por convención:

DJANGO_APPS = [
    "django.contrib.admin",         # Panel de administración auto-generado
    "django.contrib.auth",          # Sistema de autenticación (users, groups, permissions)
    "django.contrib.contenttypes",  # Framework para tipos de contenido (lo usa auth internamente)
    "django.contrib.sessions",      # Manejo de sesiones (usado por admin)
    "django.contrib.messages",      # Framework de mensajes flash
    "django.contrib.staticfiles",   # Servir archivos estáticos (CSS, JS)
]

THIRD_PARTY_APPS = [
    "rest_framework",               # Django REST Framework — convierte Django en API REST
    "corsheaders",                  # Permite que Next.js (otro dominio) llame a nuestra API
    "django_filters",               # Filtros avanzados para querysets en la API
    "drf_spectacular",              # Auto-genera documentación OpenAPI (Swagger)
]

LOCAL_APPS = [
    "apps.users",
    "apps.accounts",
    "apps.categories",
    "apps.transactions",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ──────────────────────────────────────────────
# MIDDLEWARE
# ──────────────────────────────────────────────
# 📚 Los middleware son como "capas" que procesan cada request ANTES de llegar
# a tu view, y cada response ANTES de salir al cliente.
# El orden importa: se ejecutan de arriba para abajo en el request,
# y de abajo para arriba en el response.
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",             # ← DEBE ir primero: agrega headers CORS
    "django.middleware.security.SecurityMiddleware",      # Headers de seguridad (HSTS, etc.)
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",          # Normaliza URLs (trailing slashes, etc.)
    "django.middleware.csrf.CsrfViewMiddleware",         # Protección CSRF (no aplica a API con JWT, pero lo dejamos)
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Asocia el usuario al request
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Previene clickjacking
]

# ──────────────────────────────────────────────
# URL & WSGI CONFIG
# ──────────────────────────────────────────────
ROOT_URLCONF = "config.urls"            # Django busca las rutas en config/urls.py
WSGI_APPLICATION = "config.wsgi.application"

# ──────────────────────────────────────────────
# TEMPLATES (usado por el admin panel)
# ──────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ──────────────────────────────────────────────
# DATABASE
# ──────────────────────────────────────────────
# 📚 django-environ parsea la URL de la BD automáticamente.
# Formato: postgres://USER:PASSWORD@HOST:PORT/DB_NAME
DATABASES = {
    "default": env.db("DATABASE_URL"),
}

# ──────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────
# 📚 CRÍTICO: esto le dice a Django "usa apps.users.User en vez del User default".
# DEBE configurarse ANTES de la primera migración. Si lo haces después, hay que
# borrar toda la BD y empezar de cero.
AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ──────────────────────────────────────────────
# DJANGO REST FRAMEWORK
# ──────────────────────────────────────────────
# 📚 Configuración global de DRF. Aquí definimos:
# - Cómo se autentica cada request (JWT)
# - Quién puede acceder por defecto (solo usuarios autenticados)
# - Cómo se paginan los resultados
# - Qué backend genera la documentación
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.users.firebase_backend.FirebaseAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardPagination",
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ──────────────────────────────────────────────
# FIREBASE
# ──────────────────────────────────────────────
# Ruta al JSON de la service account de Firebase (opcional si se usa
# GOOGLE_APPLICATION_CREDENTIALS como variable de entorno del sistema).
FIREBASE_CREDENTIALS_PATH = env("FIREBASE_CREDENTIALS_PATH", default="")

# ──────────────────────────────────────────────
# CORS — Cross-Origin Resource Sharing
# ──────────────────────────────────────────────
# 📚 Los navegadores bloquean requests de un dominio a otro por seguridad.
# Como Next.js corre en localhost:3000 y Django en localhost:8000,
# necesitamos decirle a Django "confía en requests que vengan de localhost:3000".
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# ──────────────────────────────────────────────
# DRF SPECTACULAR (Documentación OpenAPI)
# ──────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE": "Plutus API",
    "DESCRIPTION": "API de finanzas personales",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ──────────────────────────────────────────────
# INTERNACIONALIZACIÓN
# ──────────────────────────────────────────────
LANGUAGE_CODE = "es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True       # 📚 Siempre True — almacena fechas en UTC y convierte al mostrar

# ──────────────────────────────────────────────
# ARCHIVOS ESTÁTICOS
# ──────────────────────────────────────────────
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ──────────────────────────────────────────────
# DEFAULT PRIMARY KEY
# ──────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
