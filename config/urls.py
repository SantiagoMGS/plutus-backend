"""
📚 URLS — El "mapa de direcciones" de tu API.

Cuando alguien hace un request a tu servidor, Django busca aquí qué view
debe manejar esa URL. Es como un switch gigante:
  /admin/    → panel de administración
  /api/docs/ → documentación OpenAPI (Swagger)
  /api/auth/ → endpoints de autenticación (los crearemos en Fase 1)
  /api/...   → endpoints de cada app (los iremos agregando)
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Panel de administración de Django
    path("admin/", admin.site.urls),

    # 📚 Documentación OpenAPI — drf-spectacular genera una especificación OpenAPI
    # automáticamente a partir de tus ViewSets y Serializers.
    # /api/schema/ → JSON/YAML con la especificación
    # /api/docs/   → Swagger UI interactivo (puedes probar la API desde el navegador)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # ── URLs de las apps ──
    path("api/auth/", include("apps.users.urls")),
    # path("api/", include("apps.accounts.urls")),
    # ...
]
