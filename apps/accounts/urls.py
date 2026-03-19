"""
📚 URLS de Account — Usa un Router para generar CRUD automáticamente.

📚 CONCEPTO: DefaultRouter
En la Fase 1 definimos cada ruta manualmente con path().
Aquí usamos DefaultRouter que genera TODAS las rutas CRUD automáticamente:

    router.register("accounts", AccountViewSet)

Genera:
    GET    /api/accounts/           → AccountViewSet.list()
    POST   /api/accounts/           → AccountViewSet.create()
    GET    /api/accounts/{id}/      → AccountViewSet.retrieve()
    PUT    /api/accounts/{id}/      → AccountViewSet.update()
    PATCH  /api/accounts/{id}/      → AccountViewSet.partial_update()
    DELETE /api/accounts/{id}/      → AccountViewSet.destroy()
    GET    /api/accounts/summary/   → AccountViewSet.summary()  (nuestro @action)
"""

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("accounts", views.AccountViewSet)

urlpatterns = router.urls
