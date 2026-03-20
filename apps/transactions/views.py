"""
📚 VIEWS de Transaction — ViewSet con OwnerFilterMixin + actions custom.

La view es DELGADA: solo orquesta, la lógica está en:
- TransactionService (validaciones, summary)
- Strategy Pattern (cómo se aplica al balance)
- Observer/Signals (cuándo se actualiza el balance)
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from common.mixins import OwnerFilterMixin

from .models import Transaction
from .serializers import TransactionSerializer
from .services import TransactionService


class TransactionViewSet(OwnerFilterMixin, ModelViewSet):
    """
    📚 CRUD completo de transacciones + endpoint de resumen.

    GET    /api/transactions/         → lista (filtrada por usuario)
    POST   /api/transactions/         → crear transacción
    GET    /api/transactions/{id}/    → detalle
    DELETE /api/transactions/{id}/    → eliminar (revierte balance vía signal)
    GET    /api/transactions/summary/ → resumen (ingresos, gastos, neto)
    """

    queryset = Transaction.objects.select_related(
        "account", "destination_account", "category"
    )
    serializer_class = TransactionSerializer

    # 📚 Filtros: el frontend puede hacer GET /api/transactions/?transaction_type=INCOME
    filterset_fields = ["transaction_type", "account", "category", "date"]
    search_fields = ["description"]
    ordering_fields = ["date", "amount", "created_at"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        📚 GET /api/transactions/summary/?date_from=2026-01-01&date_to=2026-01-31

        Devuelve totales de ingresos, gastos y balance neto.
        Usa query params opcionales para filtrar rango de fechas.
        """
        filters = {
            "date_from": request.query_params.get("date_from"),
            "date_to": request.query_params.get("date_to"),
        }
        summary = TransactionService.get_summary(request.user, filters)
        return Response(summary)
