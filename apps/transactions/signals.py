"""
📚 OBSERVER PATTERN — Refactoring Guru
https://refactoring.guru/design-patterns/observer

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
¿QUÉ PROBLEMA RESUELVE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sin Observer, la view tendría que:
1. Guardar la transacción
2. Actualizar el balance de la cuenta
3. (Futuro) Enviar notificación
4. (Futuro) Actualizar estadísticas

La view termina haciendo DEMASIADAS cosas — viola Single Responsibility.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
¿CÓMO LO RESUELVE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Django signals = implementación del Observer Pattern.

- SUBJECT (quien emite): El modelo Transaction (Django lo hace automáticamente)
- EVENT: post_save (se creó/editó), post_delete (se eliminó)
- OBSERVER (quien escucha): Nuestras funciones decoradas con @receiver

Cuando Transaction.save() se ejecuta, Django automáticamente
llama a TODOS los observers registrados. La view no sabe
que existen — están completamente desacoplados.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIAGRAMA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Transaction.save()
       │
       ▼ (Django emite signal automáticamente)
  post_save signal
       │
       ├──► update_balance_on_save (Observer 1)
       ├──► (futuro) send_notification (Observer 2)
       └──► (futuro) update_statistics (Observer 3)

"""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Transaction
from .strategies import ExpenseStrategy, IncomeStrategy, TransferStrategy


# 📚 FACTORY: mapea tipo de transacción → estrategia correcta.
# Es un dict simple, pero cumple el rol de Factory Method.
STRATEGY_MAP = {
    Transaction.TransactionType.INCOME: IncomeStrategy(),
    Transaction.TransactionType.EXPENSE: ExpenseStrategy(),
    Transaction.TransactionType.TRANSFER: TransferStrategy(),
}


@receiver(post_save, sender=Transaction)
def update_balance_on_save(sender, instance, created, **kwargs):
    """
    📚 OBSERVER 1: Actualiza el balance cuando se CREA una transacción.

    @receiver(post_save, sender=Transaction) le dice a Django:
    "Cada vez que se guarde un Transaction, ejecuta esta función."

    Parámetros que Django pasa automáticamente:
    - sender: la clase del modelo (Transaction)
    - instance: el objeto que se guardó
    - created: True si es NUEVO, False si se editó
    - **kwargs: otros args que no usamos
    """
    if not created:
        # 📚 Por ahora solo manejamos creación.
        # Editar una transacción es más complejo (hay que revertir la anterior
        # y aplicar la nueva). Lo implementaremos cuando sea necesario.
        return

    strategy = STRATEGY_MAP.get(instance.transaction_type)
    if strategy:
        strategy.apply(instance)


@receiver(post_delete, sender=Transaction)
def update_balance_on_delete(sender, instance, **kwargs):
    """
    📚 OBSERVER 2: Revierte el efecto cuando se ELIMINA una transacción.

    Si borras un ingreso de $100, hay que RESTAR $100 del balance.
    La strategy se encarga de saber cómo revertir cada tipo.
    """
    strategy = STRATEGY_MAP.get(instance.transaction_type)
    if strategy:
        strategy.revert(instance)
