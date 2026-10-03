# transaction_adapter.py

from dataclasses import dataclass

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


@dataclass(frozen=True, slots=True)
class TransactionAdapter:
    """Adapter to convert external freelance income into Transaction."""

    external_transaction: object

    def __init__(self, external_transaction):
        object.__setattr__(self, "external_transaction", external_transaction)

    def _validate_external(self):
        """Validate required external fields before adaptation."""
        ext = self.external_transaction

        required_fields = ("amount", "invoice_id", "description", "typ")
        for field in required_fields:
            if not hasattr(ext, field):
                raise ValueError(f"external transaction missing required field: {field}")

        if str(ext.typ).lower() != "income":
            raise ValueError("external transaction type must be income")

    def to_transaction(self):
        """Convert an external transaction to a standard Transaction."""
        self._validate_external()
        return Transaction(self.external_transaction.amount, TransactionCategory.INCOME)
