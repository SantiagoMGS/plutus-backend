"""
📚 PAGINATION — Configuración de paginación para la API.

Sin paginación, si tienes 10,000 transacciones, un GET /api/transactions/
devolvería las 10,000 de golpe → lento y consume mucha memoria.

Con paginación: devuelve 20 por página, y el frontend pide la siguiente
con ?page=2. La response incluye count, next, previous para navegar.
"""

from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    📚 Ejemplo de response paginada:
    {
        "count": 150,                              ← total de objetos
        "next": "http://localhost:8000/api/transactions/?page=2",
        "previous": null,
        "results": [...]                           ← los 20 objetos de esta página
    }
    """

    page_size = 20                     # Objetos por página por defecto
    page_size_query_param = "page_size"  # El frontend puede pedir más: ?page_size=50
    max_page_size = 100                 # Máximo permitido para evitar abusos
