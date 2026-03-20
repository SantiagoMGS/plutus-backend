"""
📚 MODELO TRANSACTION — Registra cada movimiento financiero.

Cada transacción representa un evento:
- INCOME: dinero que ENTRA a una cuenta (salario, venta, etc.)
- EXPENSE: dinero que SALE de una cuenta (compra, pago, etc.)
- TRANSFER: dinero que se MUEVE entre dos cuentas del mismo usuario

📚 CONCEPTOS NUEVOS:
- related_name con "+" → indica que NO necesitamos la relación inversa
- destination_account → solo se usa en transferencias
- La lógica de cómo afecta al balance NO está aquí — eso lo maneja Strategy Pattern
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class Transaction(models.Model):

    class TransactionType(models.TextChoices):
        INCOME = "INCOME", "Ingreso"
        EXPENSE = "EXPENSE", "Gasto"
        TRANSFER = "TRANSFER", "Transferencia"

    # ──────────────────────────────────────────────
    # RELACIONES
    # ──────────────────────────────────────────────

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    # 📚 Cuenta ORIGEN: de dónde sale el dinero (gasto/transferencia)
    # o a dónde entra (ingreso).
    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    # 📚 Cuenta DESTINO: solo se usa en transferencias.
    # null=True porque ingresos y gastos no tienen cuenta destino.
    # PROTECT evita borrar una cuenta que es destino de transferencias.
    destination_account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.PROTECT,
        related_name="incoming_transfers",
        null=True,
        blank=True,
    )

    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.SET_NULL,
        related_name="transactions",
        null=True,
        blank=True,
    )

    # ──────────────────────────────────────────────
    # CAMPOS
    # ──────────────────────────────────────────────

    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
    )

    # 📚 amount SIEMPRE es positivo. El tipo de transacción determina
    # si suma o resta al balance. Esto simplifica mucho la lógica.
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    description = models.CharField(max_length=255, blank=True, default="")

    # 📚 date vs created_at:
    # - date: cuándo OCURRIÓ la transacción (puede ser en el pasado)
    # - created_at: cuándo se REGISTRÓ en el sistema (automático)
    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transactions"
        verbose_name = "transacción"
        verbose_name_plural = "transacciones"
        ordering = ["-date", "-created_at"]
        # 📚 indexes: mejoran la velocidad de búsqueda en campos frecuentes.
        # Sin índice, PostgreSQL escanea TODA la tabla. Con índice, va directo.
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["account", "date"]),
            models.Index(fields=["transaction_type"]),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} ${self.amount} — {self.description or 'Sin descripción'}"
