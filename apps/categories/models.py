"""
📚 MODELO CATEGORY — Clasifica transacciones en grupos.

Cada transacción pertenece a una categoría (Comida, Transporte, Salario, etc.)
Esto permite generar reportes como "¿Cuánto gasté en comida este mes?"

📚 CONCEPTO NUEVO: ForeignKey nullable (null=True, blank=True)
- Si user=NULL → categoría del SISTEMA (visible para todos, no editable)
- Si user=FK → categoría CUSTOM de ese usuario (solo él la ve)
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class Category(models.Model):

    class CategoryType(models.TextChoices):
        INCOME = "INCOME", "Ingreso"
        EXPENSE = "EXPENSE", "Gasto"

    name = models.CharField(max_length=100)

    # 📚 El "tipo" define si esta categoría es para ingresos o gastos.
    # Así evitamos que alguien ponga "Salario" como gasto.
    category_type = models.CharField(
        max_length=10,
        choices=CategoryType.choices,
    )

    icon = models.CharField(max_length=50, default="tag")
    color = models.CharField(max_length=7, default="#6B7280")

    # 📚 is_default=True → categoría del sistema (precargada, no editable por usuarios)
    is_default = models.BooleanField(default=False)

    # 📚 user=NULL → categoría del sistema (global)
    # user=FK → categoría custom de ese usuario
    # null=True permite que la BD almacene NULL
    # blank=True permite que el serializer acepte campo vacío
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "categories"
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["name"]
        # 📚 unique_together: evita que un usuario tenga dos categorías con el mismo nombre Y tipo.
        # Un usuario puede tener "Comida" EXPENSE y "Comida" INCOME, pero no dos "Comida" EXPENSE.
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name", "category_type"],
                name="unique_category_per_user",
            ),
        ]

    def __str__(self):
        prefix = "🌐" if self.is_default else "👤"
        return f"{prefix} {self.name} ({self.get_category_type_display()})"
