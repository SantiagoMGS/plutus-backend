"""
📚 SERIALIZERS de Account.

Aquí usamos dos serializers:
1. AccountSerializer — para CRUD (crear/editar/ver cuentas)
2. AccountSummarySerializer — versión resumida para listas y reportes

📚 CONCEPTO NUEVO: SerializerMethodField
Es un campo "calculado" — no existe en el modelo, se calcula on-the-fly
con un método get_<nombre_del_campo>(). Perfecto para datos derivados
como "crédito disponible".
"""

from rest_framework import serializers

from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    """
    📚 Serializer completo para CRUD de cuentas.

    Fíjate que 'user' NO está en fields — el usuario se asigna
    automáticamente en OwnerFilterMixin.perform_create().
    El frontend NUNCA envía user_id. Eso previene que alguien
    cree una cuenta a nombre de otro usuario.
    """

    # 📚 SerializerMethodField: campo de SOLO LECTURA calculado.
    # DRF busca un método llamado get_available_credit() para obtener el valor.
    available_credit = serializers.SerializerMethodField()

    # 📚 source="get_account_type_display": le dice a DRF "lee el valor
    # del método get_account_type_display() del modelo".
    # Así en vez de devolver "CREDIT_CARD", devuelve "Tarjeta de Crédito".
    account_type_display = serializers.CharField(
        source="get_account_type_display",
        read_only=True,
    )

    class Meta:
        model = Account
        fields = (
            "id",
            "name",
            "account_type",
            "account_type_display",
            "currency",
            "balance",
            "color",
            "icon",
            "credit_limit",
            "interest_rate",
            "cut_off_day",
            "payment_day",
            "available_credit",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "balance", "created_at", "updated_at")
        # 📚 balance es read_only porque NO se modifica directamente.
        # Se actualiza a través de transacciones (Fase 4).

    def get_available_credit(self, obj: Account) -> float | None:
        """
        📚 Este método alimenta al campo 'available_credit'.
        DRF lo llama automáticamente por convención: get_<field_name>().
        """
        return obj.available_credit

    def validate(self, attrs):
        """
        📚 Validación condicional: si es tarjeta de crédito,
        credit_limit es obligatorio.
        """
        account_type = attrs.get("account_type", getattr(self.instance, "account_type", None))

        if account_type == Account.AccountType.CREDIT_CARD:
            if not attrs.get("credit_limit") and not getattr(self.instance, "credit_limit", None):
                raise serializers.ValidationError({
                    "credit_limit": "El cupo es obligatorio para tarjetas de crédito.",
                })
        return attrs
