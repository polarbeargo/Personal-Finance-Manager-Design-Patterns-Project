import unittest

from transaction.external_income_transaction import ExternalFreelanceIncome
from transaction.transaction_adapter import TransactionAdapter
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestTransactionAdapter(unittest.TestCase):

    def test_adapter_converts_freelance_income(self):
        ext_txn = ExternalFreelanceIncome(
            500, "INV-12345", "Website development")
        adapter = TransactionAdapter(ext_txn)
        txn = adapter.to_transaction()
        self.assertEqual(txn, Transaction(500, TransactionCategory.INCOME))

    def test_adapter_rejects_non_income_type(self):
        ext_txn = ExternalFreelanceIncome(
            500, "INV-12345", "Website development")
        ext_txn.typ = "expense"

        adapter = TransactionAdapter(ext_txn)
        with self.assertRaises(ValueError):
            adapter.to_transaction()

    def test_adapter_rejects_missing_required_fields(self):
        class IncompleteExternalTransaction:
            def __init__(self):
                self.amount = 100
                self.typ = "income"

        adapter = TransactionAdapter(IncompleteExternalTransaction())
        with self.assertRaises(ValueError):
            adapter.to_transaction()


if __name__ == "__main__":
    unittest.main()
