from dataclasses import dataclass
from decimal import Decimal
from decimal import InvalidOperation

from transaction.transaction_category import TransactionCategory


@dataclass(frozen=True, slots=True)
class Transaction:
    """Represents a financial transaction with an amount and category."""

    amount: Decimal
    category: TransactionCategory

    def __init__(self, amount, category: TransactionCategory):
        if not isinstance(category, TransactionCategory):
            raise ValueError("category must be a TransactionCategory")

        try:
            normalized_amount = Decimal(str(amount))
        except (TypeError, ValueError, InvalidOperation) as exc:
            raise ValueError("amount must be numeric") from exc

        if not normalized_amount.is_finite():
            raise ValueError("amount must be finite")

        object.__setattr__(self, "amount", normalized_amount)
        object.__setattr__(self, "category", category)

    def __str__(self):
        return f"Transaction(${self.amount}, category='{self.category}')"

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return NotImplemented

        return self.amount == other.amount and self.category == other.category
