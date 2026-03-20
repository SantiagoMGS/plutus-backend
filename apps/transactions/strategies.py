"""
📚 STRATEGY PATTERN — Refactoring Guru
https://refactoring.guru/design-patterns/strategy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
¿QUÉ PROBLEMA RESUELVE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sin Strategy tendríamos un bloque if/elif gigante:

    def apply_transaction(transaction):
        if transaction.type == "INCOME":
            account.balance += amount
        elif transaction.type == "EXPENSE":
            account.balance -= amount
        elif transaction.type == "TRANSFER":
            source.balance -= amount
            dest.balance += amount

Parece simple con 3 tipos, PERO:
- Si agregamos "LOAN_PAYMENT" tenemos que modificar el mismo bloque
- Si agregamos "RECURRING_EXPENSE" lo mismo
- Viola el principio Open/Closed: el código debería estar ABIERTO
  a extensión pero CERRADO a modificación

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
¿CÓMO LO RESUELVE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Definimos una INTERFAZ (ABC) que dice "toda estrategia debe tener apply() y revert()"
2. Cada tipo de transacción implementa esa interfaz a su manera
3. El servicio NO sabe cuál estrategia usa — solo llama strategy.apply()

Para agregar "LOAN_PAYMENT" solo creamos LoanPaymentStrategy y la
registramos. NO tocamos código existente.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIAGRAMA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  TransactionService (Context)
         │
         ▼
  TransactionStrategy (ABC / Interface)
     ┌────┼──────────┐
     ▼    ▼          ▼
  Income  Expense  Transfer
  Strategy Strategy Strategy

"""

from abc import ABC, abstractmethod
from decimal import Decimal


class TransactionStrategy(ABC):
    """
    📚 ABC = Abstract Base Class (clase abstracta de Python).

    Es como una "interface" en TypeScript/Java.
    Define un CONTRATO: toda clase que herede de TransactionStrategy
    DEBE implementar apply() y revert().

    Si no los implementa → Python lanza TypeError al instanciarla.
    """

    @abstractmethod
    def apply(self, transaction) -> None:
        """
        Aplicar la transacción al balance de la(s) cuenta(s).
        Se llama al CREAR una transacción.
        """

    @abstractmethod
    def revert(self, transaction) -> None:
        """
        Revertir el efecto de la transacción (des-hacer).
        Se llama al ELIMINAR una transacción.
        """


class IncomeStrategy(TransactionStrategy):
    """
    📚 Ingreso: el dinero ENTRA a la cuenta.
    apply() → suma al balance
    revert() → resta del balance (deshacer)
    """

    def apply(self, transaction) -> None:
        account = transaction.account
        account.balance += transaction.amount
        account.save(update_fields=["balance", "updated_at"])

    def revert(self, transaction) -> None:
        account = transaction.account
        account.balance -= transaction.amount
        account.save(update_fields=["balance", "updated_at"])


class ExpenseStrategy(TransactionStrategy):
    """
    📚 Gasto: el dinero SALE de la cuenta.
    apply() → resta del balance
    revert() → suma al balance (deshacer)
    """

    def apply(self, transaction) -> None:
        account = transaction.account
        account.balance -= transaction.amount
        account.save(update_fields=["balance", "updated_at"])

    def revert(self, transaction) -> None:
        account = transaction.account
        account.balance += transaction.amount
        account.save(update_fields=["balance", "updated_at"])


class TransferStrategy(TransactionStrategy):
    """
    📚 Transferencia: el dinero se MUEVE de una cuenta a otra.
    apply() → resta de origen, suma a destino
    revert() → suma a origen, resta de destino (deshacer)

    Nota: destination_account DEBE existir para transferencias.
    """

    def apply(self, transaction) -> None:
        source = transaction.account
        destination = transaction.destination_account

        source.balance -= transaction.amount
        source.save(update_fields=["balance", "updated_at"])

        destination.balance += transaction.amount
        destination.save(update_fields=["balance", "updated_at"])

    def revert(self, transaction) -> None:
        source = transaction.account
        destination = transaction.destination_account

        source.balance += transaction.amount
        source.save(update_fields=["balance", "updated_at"])

        destination.balance -= transaction.amount
        destination.save(update_fields=["balance", "updated_at"])
