from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory

_REVERSED_CATEGORY = {
    TransactionCategory.INCOME: TransactionCategory.EXPENSE,
    TransactionCategory.EXPENSE: TransactionCategory.INCOME,
}


class Command(ABC):
    """An action that can be executed and undone."""

    __slots__ = ()

    @abstractmethod
    def execute(self):
        """Perform the action."""

    @abstractmethod
    def undo(self):
        """Reverse the action."""


@dataclass(frozen=True, slots=True)
class ApplyTransactionCommand(Command):
    """Apply a transaction and support its reversal."""

    balance: object
    transaction: Transaction

    def execute(self):
        self.balance.apply_transaction(self.transaction)

    def undo(self):
        reversed_category = _REVERSED_CATEGORY.get(self.transaction.category)
        if reversed_category is None:
            raise ValueError("Invalid transaction category")

        self.balance.apply_transaction(
            Transaction(self.transaction.amount, reversed_category)
        )
