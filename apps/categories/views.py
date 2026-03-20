"""
📚 VIEWS de Category — ViewSet con lógica especial de queryset.

A diferencia de Account (donde OwnerFilterMixin filtra por user),
aquí necesitamos lógica custom:
- GET (list/retrieve): muestra categorías del sistema + custom del usuario
- POST/PATCH/DELETE: solo aplica a las custom del usuario (las del sistema son read-only)

📚 CONCEPTO NUEVO: Q objects
Django usa Q() para hacer queries con OR:
    Q(is_default=True) | Q(user=request.user)
Esto genera SQL: WHERE is_default=TRUE OR user_id=1
"""

from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    filterset_fields = ["category_type"]
    search_fields = ["name"]
    ordering_fields = ["name"]

    def get_queryset(self):
        """
        📚 Muestra categorías del sistema (is_default=True, user=NULL)
        + categorías custom del usuario autenticado.

        Q(is_default=True) → categorías globales del sistema
        Q(user=self.request.user) → categorías custom de este usuario
        | → OR (unión de ambos conjuntos)
        """
        return Category.objects.filter(
            Q(is_default=True) | Q(user=self.request.user)
        )

    def perform_create(self, serializer):
        """
        📚 Al crear una categoría, automáticamente:
        - Asigna user=request.user
        - is_default=False (un usuario no puede crear categorías del sistema)
        """
        serializer.save(user=self.request.user, is_default=False)

    def update(self, request, *args, **kwargs):
        """📚 No se pueden editar categorías del sistema."""
        category = self.get_object()
        if category.is_default:
            return Response(
                {"detail": "No se pueden editar categorías del sistema."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """📚 No se pueden borrar categorías del sistema."""
        category = self.get_object()
        if category.is_default:
            return Response(
                {"detail": "No se pueden eliminar categorías del sistema."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
