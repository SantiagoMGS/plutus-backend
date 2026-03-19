"""
📚 MODELO ACCOUNT — Cuentas bancarias, wallets, tarjetas de crédito, efectivo.

Cada usuario puede tener múltiples cuentas. Cada cuenta tiene un balance
que se actualiza automáticamente cuando se registran transacciones (Fase 4).

📚 NUEVOS CONCEPTOS:
- TextChoices: enum para definir opciones válidas (como un enum de TypeScript)
- DecimalField: para dinero, SIEMPRE usar Decimal, nunca Float
- ForeignKey: relación "muchos a uno" (un User tiene muchas Accounts)
- related_name: nombre para acceder a la relación inversa (user.accounts.all())
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class Account(models.Model):
    """
    Cuenta financiera del usuario.

    📚 models.Model es la clase base de todos los modelos Django.
    Django automáticamente crea:
    - Un campo `id` (BigAutoField, autoincremental)
    - La tabla en la BD cuando corres `migrate`
    """

    # ──────────────────────────────────────────────
    # ENUMS (TextChoices)
    # ──────────────────────────────────────────────
    # 📚 TextChoices es como un enum. Define las opciones válidas para un campo.
    # El primer valor es lo que se guarda en la BD, el segundo es lo que se muestra.
    # En TypeScript sería: type AccountType = "BANK" | "WALLET" | "CREDIT_CARD" | "CASH"

    class AccountType(models.TextChoices):
        BANK = "BANK", "Cuenta Bancaria"
        WALLET = "WALLET", "Billetera Digital"
        CREDIT_CARD = "CREDIT_CARD", "Tarjeta de Crédito"
        CASH = "CASH", "Efectivo"

    class Currency(models.TextChoices):
        COP = "COP", "Peso Colombiano"
        USD = "USD", "Dólar Estadounidense"
        EUR = "EUR", "Euro"

    # ──────────────────────────────────────────────
    # CAMPOS PRINCIPALES
    # ──────────────────────────────────────────────

    # 📚 ForeignKey = relación "muchos a uno".
    # Cada cuenta tiene UN usuario dueño, pero un usuario puede tener MUCHAS cuentas.
    # on_delete=CASCADE: si se borra el usuario, se borran sus cuentas.
    # related_name="accounts": permite hacer user.accounts.all() para obtener las cuentas del usuario.
    # settings.AUTH_USER_MODEL: referencia al User model (mejor que importar directamente).
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts",
    )

    name = models.CharField(
        max_length=100,
        help_text="Nombre de la cuenta (ej: 'Bancolombia Ahorros', 'Nequi')",
    )

    # 📚 choices=AccountType.choices le dice a Django "solo acepta estos valores".
    # Si intentas guardar account_type="BITCOIN", Django lanza un ValidationError.
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.COP,
    )

    # 📚 DecimalField para dinero:
    # max_digits=15: hasta 15 dígitos en total (ej: 999,999,999,999.99)
    # decimal_places=2: siempre 2 decimales
    # NUNCA uses FloatField para dinero — los floats tienen errores de precisión.
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Balance actual de la cuenta",
    )

    color = models.CharField(
        max_length=7,
        default="#4F46E5",
        help_text="Color en formato hex (ej: '#4F46E5')",
    )

    icon = models.CharField(
        max_length=50,
        default="wallet",
        help_text="Nombre del ícono (ej: 'wallet', 'bank', 'credit-card')",
    )

    # ──────────────────────────────────────────────
    # CAMPOS EXCLUSIVOS DE TARJETAS DE CRÉDITO
    # ──────────────────────────────────────────────
    # 📚 blank=True, null=True: estos campos son OPCIONALES.
    # Solo aplican cuando account_type="CREDIT_CARD".
    # - null=True: la BD permite NULL
    # - blank=True: los formularios/serializers permiten campo vacío

    credit_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cupo total de la tarjeta de crédito",
    )

    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Tasa de interés mensual (%)",
    )

    cut_off_day = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Día de corte de la tarjeta (1-31)",
    )

    payment_day = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Día límite de pago (1-31)",
    )

    # ──────────────────────────────────────────────
    # SOFT DELETE & TIMESTAMPS
    # ──────────────────────────────────────────────
    # 📚 Soft delete: en vez de borrar la cuenta (y perder el historial de transacciones),
    # la marcamos como "inactiva". Así las transacciones pasadas siguen existiendo.
    is_active = models.BooleanField(default=True)

    # 📚 auto_now_add=True: se asigna automáticamente al crear el objeto (y no se puede cambiar)
    # auto_now=True: se actualiza automáticamente cada vez que se guarda el objeto
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts"
        verbose_name = "cuenta"
        verbose_name_plural = "cuentas"
        # 📚 ordering: orden por defecto cuando haces Account.objects.all()
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"
        # 📚 get_<field>_display() es un método mágico de Django.
        # Si account_type="CREDIT_CARD", devuelve "Tarjeta de Crédito" (el label del choice)

    @property
    def available_credit(self):
        """
        📚 @property convierte un método en un atributo.
        En vez de account.available_credit(), haces account.available_credit

        Solo aplica a tarjetas de crédito: cupo - balance usado.
        """
        if self.account_type == self.AccountType.CREDIT_CARD and self.credit_limit:
            return self.credit_limit - abs(self.balance)
        return None
