"""
📚 FACTORY METHOD PATTERN — Refactoring Guru
https://refactoring.guru/design-patterns/factory-method

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
¿QUÉ PROBLEMA RESUELVE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

La view no debería saber qué estrategia usar. Solo dice:
"Quiero crear una transacción de tipo INCOME" y el Service
se encarga de crear el objeto correcto.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
¿CÓMO LO RESUELVE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TransactionService.get_strategy() es el Factory Method:
recibe un tipo y CREA/DEVUELVE la estrategia correcta.

El Service (Context) trabaja con la interfaz TransactionStrategy,
nunca directamente con IncomeStrategy/ExpenseStrategy.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FLUJO COMPLETO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  View → "Crea transacción tipo EXPENSE"
    │
    ▼
  TransactionService.create_transaction()
    │
    ├── 1. Valida datos
    ├── 2. get_strategy("EXPENSE") → ExpenseStrategy  [Factory Method]
    ├── 3. Transaction.objects.create(...)             [Crea en BD]
    └── 4. (signal post_save se dispara automáticamente)
              └── strategy.apply(transaction)          [Observer]
                    └── account.balance -= amount      [Strategy]
"""

from django.db import transaction as db_transaction
from django.db.models import Sum
from rest_framework.exceptions import ValidationError

from .models import Transaction
from .strategies import (
    ExpenseStrategy,
    IncomeStrategy,
    TransactionStrategy,
    TransferStrategy,
)


class TransactionService:
    """
    📚 Service Layer + Factory Method.

    Centraliza toda la lógica de negocio de transacciones.
    La view solo llama a los métodos del servicio.
    """

    # ──────────────────────────────────────────────
    # FACTORY METHOD
    # ──────────────────────────────────────────────

    # 📚 Mapeo tipo → estrategia. Para agregar un nuevo tipo,
    # solo creas la clase y la agregas aquí. No tocas nada más.
    _strategies: dict[str, TransactionStrategy] = {
        Transaction.TransactionType.INCOME: IncomeStrategy(),
        Transaction.TransactionType.EXPENSE: ExpenseStrategy(),
        Transaction.TransactionType.TRANSFER: TransferStrategy(),
    }

    @classmethod
    def get_strategy(cls, transaction_type: str) -> TransactionStrategy:
        """
        📚 FACTORY METHOD: recibe un tipo y devuelve la estrategia correcta.

        En Refactoring Guru, el Factory Method es un método que crea objetos
        sin especificar la clase exacta. Aquí lo usamos con un dict porque
        Python favorece la simplicidad, pero el principio es el mismo:
        el caller no sabe qué clase concreta recibe.
        """
        strategy = cls._strategies.get(transaction_type)
        if not strategy:
            raise ValidationError(
                {"transaction_type": f"Tipo no soportado: {transaction_type}"}
            )
        return strategy

    # ──────────────────────────────────────────────
    # BUSINESS LOGIC
    # ──────────────────────────────────────────────

    @staticmethod
    def validate_transfer(data: dict) -> None:
        """Valida que una transferencia tenga cuenta destino diferente a la origen."""
        if data.get("transaction_type") != Transaction.TransactionType.TRANSFER:
            return

        destination = data.get("destination_account")
        if not destination:
            raise ValidationError(
                {"destination_account": "Las transferencias requieren cuenta destino."}
            )
        if data.get("account") == destination:
            raise ValidationError(
                {"destination_account": "La cuenta destino debe ser diferente a la origen."}
            )

    @staticmethod
    def validate_category_type(data: dict) -> None:
        """Valida que la categoría coincida con el tipo de transacción."""
        category = data.get("category")
        tx_type = data.get("transaction_type")

        if not category or tx_type == Transaction.TransactionType.TRANSFER:
            return

        expected_cat_type = {
            Transaction.TransactionType.INCOME: "INCOME",
            Transaction.TransactionType.EXPENSE: "EXPENSE",
        }.get(tx_type)

        if category.category_type != expected_cat_type:
            raise ValidationError(
                {"category": f"La categoría debe ser de tipo {expected_cat_type}."}
            )

    @staticmethod
    def get_summary(user, filters: dict | None = None):
        """
        📚 Resumen de transacciones del usuario.
        Usa aggregate() y Sum() para calcular totales directamente en SQL.
        """
        qs = Transaction.objects.filter(user=user)

        if filters:
            if filters.get("date_from"):
                qs = qs.filter(date__gte=filters["date_from"])
            if filters.get("date_to"):
                qs = qs.filter(date__lte=filters["date_to"])

        income = (
            qs.filter(transaction_type=Transaction.TransactionType.INCOME)
            .aggregate(total=Sum("amount"))["total"]
        ) or 0

        expenses = (
            qs.filter(transaction_type=Transaction.TransactionType.EXPENSE)
            .aggregate(total=Sum("amount"))["total"]
        ) or 0

        return {
            "total_income": income,
            "total_expenses": expenses,
            "net": income - expenses,
            "transaction_count": qs.count(),
        }
