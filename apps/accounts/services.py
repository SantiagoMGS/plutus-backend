"""
📚 SERVICE LAYER — Lógica de negocio de Accounts.

Estas operaciones no son CRUD simple (eso lo hace el ViewSet).
El service contiene lógica más compleja que el ViewSet no debería tener.
"""

from __future__ import annotations

from decimal import Decimal

from django.db.models import Sum

from .models import Account


class AccountService:

    @staticmethod
    def get_total_balance(user) -> dict:
        """
        📚 Calcula el balance total agrupado por moneda.

        Usa aggregate() para hacer un SUM directamente en la BD
        (en vez de traer todas las cuentas a Python y sumar ahí).

        Ejemplo de retorno:
        {"COP": Decimal("5000000.00"), "USD": Decimal("1500.00")}
        """
        accounts = Account.objects.filter(user=user, is_active=True)
        totals = {}
        for currency in accounts.values_list("currency", flat=True).distinct():
            total = accounts.filter(currency=currency).aggregate(
                total=Sum("balance")
            )["total"] or Decimal("0")
            totals[currency] = total
        return totals

    @staticmethod
    def get_available_credit(user) -> Decimal:
        """Total de crédito disponible en todas las tarjetas del usuario."""
        credit_cards = Account.objects.filter(
            user=user,
            account_type=Account.AccountType.CREDIT_CARD,
            is_active=True,
            credit_limit__isnull=False,
        )
        total_limit = credit_cards.aggregate(total=Sum("credit_limit"))["total"] or Decimal("0")
        total_used = credit_cards.aggregate(total=Sum("balance"))["total"] or Decimal("0")
        return total_limit - abs(total_used)

    @staticmethod
    def soft_delete(account: Account) -> Account:
        """
        📚 Soft delete: no borra la cuenta, solo la desactiva.
        Así las transacciones vinculadas a esta cuenta siguen existiendo.
        """
        account.is_active = False
        account.save(update_fields=["is_active"])
        return account
