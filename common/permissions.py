"""
📚 PERMISSIONS — Permisos personalizados para DRF.

En DRF, un "permission" decide si un request tiene acceso a un recurso.
DRF ya incluye algunos:
- IsAuthenticated: solo usuarios logueados
- IsAdminUser: solo superusuarios

Nosotros creamos IsOwner: "solo el dueño del objeto puede verlo/editarlo".
Esto garantiza que un usuario NO pueda ver las transacciones de otro.
"""

from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    📚 Permiso que verifica que el objeto pertenece al usuario autenticado.

    DRF llama a has_object_permission() automáticamente cuando usas
    retrieve(), update(), destroy() en un ViewSet.

    Ejemplo: si haces GET /api/accounts/5/, DRF carga el Account con id=5
    y luego llama a has_object_permission(request, view, account).
    Si account.user != request.user → 403 Forbidden.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
