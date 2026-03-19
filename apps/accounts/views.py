"""
📚 VIEWS de Account — ViewSet con CRUD completo.

📚 CONCEPTO: ModelViewSet
Hereda de GenericAPIView + CreateModelMixin + RetrieveModelMixin +
UpdateModelMixin + DestroyModelMixin + ListModelMixin.
= Te da list, create, retrieve, update, partial_update, destroy.

📚 CONCEPTO: @action (decorador)
Permite agregar endpoints EXTRAS al ViewSet más allá del CRUD estándar.
Ej: GET /api/accounts/summary/ → balance total por moneda.

📚 CONCEPTO: OwnerFilterMixin (patrón Template Method)
Nuestro mixin de common/mixins.py se aplica aquí:
- get_queryset() filtra automáticamente por request.user
- perform_create() asigna automáticamente user=request.user
El ViewSet no necesita preocuparse por filtrar — el mixin lo hace.
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from common.mixins import OwnerFilterMixin
from common.permissions import IsOwner

from .models import Account
from .serializers import AccountSerializer
from .services import AccountService


class AccountViewSet(OwnerFilterMixin, ModelViewSet):
    """
    📚 ViewSet para CRUD de cuentas.

    OwnerFilterMixin va PRIMERO en la herencia (MRO — Method Resolution Order).
    Esto significa que cuando DRF llame a get_queryset(), primero busca
    en OwnerFilterMixin, y ahí está nuestro filtro por usuario.

    Endpoints generados automáticamente por ModelViewSet + Router:
      GET    /api/accounts/          → list (todas mis cuentas)
      POST   /api/accounts/          → create (crear cuenta)
      GET    /api/accounts/{id}/     → retrieve (ver una cuenta)
      PATCH  /api/accounts/{id}/     → partial_update (editar)
      DELETE /api/accounts/{id}/     → destroy (borrar)

    Endpoints extra con @action:
      GET    /api/accounts/summary/  → balance total por moneda
    """

    queryset = Account.objects.filter(is_active=True)
    serializer_class = AccountSerializer
    permission_classes = [IsOwner]

    # 📚 filterset_fields: django-filter genera filtros automáticos para estos campos.
    # Permite: GET /api/accounts/?account_type=BANK&currency=COP
    filterset_fields = ["account_type", "currency"]

    # 📚 search_fields: habilita búsqueda por texto con ?search=nequi
    search_fields = ["name"]

    # 📚 ordering_fields: permite ordenar con ?ordering=balance o ?ordering=-balance
    ordering_fields = ["balance", "name", "created_at"]

    def destroy(self, request, *args, **kwargs):
        """
        📚 Sobreescribimos destroy() para hacer soft delete.
        En vez de account.delete() (que borra de la BD), usamos
        AccountService.soft_delete() que solo marca is_active=False.
        """
        account = self.get_object()
        AccountService.soft_delete(account)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        📚 @action es un decorador que agrega endpoints extras al ViewSet.
        - detail=False: la URL es /api/accounts/summary/ (sin ID, es colección)
        - detail=True: sería /api/accounts/{id}/summary/ (con ID, un objeto)

        Este endpoint devuelve el balance total por moneda y crédito disponible.
        """
        return Response({
            "balances_by_currency": AccountService.get_total_balance(request.user),
            "available_credit": AccountService.get_available_credit(request.user),
        })
