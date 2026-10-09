import unittest
from decimal import Decimal

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestTransaction(unittest.TestCase):

    def test_transaction_creation(self):
        t = Transaction(100, TransactionCategory.EXPENSE)
        self.assertEqual(t.amount, Decimal("100"))
        self.assertEqual(t.category, TransactionCategory.EXPENSE)

    def test_transaction_str(self):
        t = Transaction(50, TransactionCategory.INCOME)
        self.assertEqual(
            str(t), "Transaction($50, category='TransactionCategory.INCOME')")

    def test_transaction_equality(self):
        t1 = Transaction(20, TransactionCategory.EXPENSE)
        t2 = Transaction(20, TransactionCategory.EXPENSE)
        t3 = Transaction(30, TransactionCategory.EXPENSE)
        self.assertEqual(t1, t2)
        self.assertNotEqual(t1, t3)

    def test_transaction_rejects_non_finite_amount(self):
        with self.assertRaises(ValueError):
            Transaction("NaN", TransactionCategory.INCOME)


if __name__ == "__main__":
    unittest.main()
