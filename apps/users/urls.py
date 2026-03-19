"""
📚 URLS de la app Users — Define las rutas de autenticación.

Estas URLs se "montan" bajo /api/auth/ (configurado en config/urls.py).
Entonces la ruta completa para registro es: /api/auth/register/

📚 SimpleJWT provee dos views listas:
- TokenObtainPairView → POST con username+password, devuelve access+refresh tokens (login)
- TokenRefreshView → POST con refresh token, devuelve nuevo access token

Nosotros no necesitamos escribir la lógica de login — SimpleJWT ya lo hace.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

# 📚 app_name es usado por Django para hacer "reverse" de URLs.
# Ej: reverse("users:register") → "/api/auth/register/"
app_name = "users"

urlpatterns = [
    # ── Auth endpoints ──
    # 📚 TokenObtainPairView: envías {"username": "...", "password": "..."}
    #    y te devuelve {"access": "<jwt>", "refresh": "<jwt>"}
    path("login/", TokenObtainPairView.as_view(), name="login"),

    # 📚 TokenRefreshView: envías {"refresh": "<jwt>"}
    #    y te devuelve {"access": "<nuevo_jwt>"}
    #    Esto se usa cuando el access token expira (cada 30 min)
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # Nuestros endpoints custom
    path("register/", views.RegisterView.as_view(), name="register"),
    path("me/", views.ProfileView.as_view(), name="profile"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
]
