"""
📚 SERIALIZERS de Transaction.

Serializer para CRUD de transacciones.
Las validaciones de negocio se delegan al TransactionService (Service Layer).
"""

from rest_framework import serializers

from apps.accounts.models import Account

from .models import Transaction
from .services import TransactionService


class TransactionSerializer(serializers.ModelSerializer):
    """
    📚 Maneja la serialización y validación de transacciones.

    Campos de SOLO LECTURA para el frontend:
    - transaction_type_display: "Ingreso" en vez de "INCOME"
    - account_name: nombre de la cuenta origen
    - destination_account_name: nombre de la cuenta destino (solo transferencias)
    - category_name: nombre de la categoría
    """

    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display",
        read_only=True,
    )

    account_name = serializers.CharField(
        source="account.name",
        read_only=True,
    )

    destination_account_name = serializers.CharField(
        source="destination_account.name",
        read_only=True,
        default=None,
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
        default=None,
    )

    class Meta:
        model = Transaction
        fields = (
            "id",
            "transaction_type",
            "transaction_type_display",
            "amount",
            "description",
            "date",
            "account",
            "account_name",
            "destination_account",
            "destination_account_name",
            "category",
            "category_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate_amount(self, value):
        """📚 El monto siempre debe ser positivo."""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0.")
        return value

    def validate_account(self, value):
        """📚 La cuenta debe pertenecer al usuario autenticado."""
        if value.user != self.context["request"].user:
            raise serializers.ValidationError("Esta cuenta no te pertenece.")
        if not value.is_active:
            raise serializers.ValidationError("Esta cuenta está desactivada.")
        return value

    def validate_destination_account(self, value):
        """📚 La cuenta destino también debe ser del usuario."""
        if value is None:
            return value
        if value.user != self.context["request"].user:
            raise serializers.ValidationError("Esta cuenta no te pertenece.")
        if not value.is_active:
            raise serializers.ValidationError("Esta cuenta está desactivada.")
        return value

    def validate(self, attrs):
        """
        📚 Validación cruzada que involucra múltiples campos.
        Delega al Service para mantener la lógica en un solo lugar.
        """
        TransactionService.validate_transfer(attrs)
        TransactionService.validate_category_type(attrs)
        return attrs
