import threading
import unittest
from decimal import Decimal

from balance.balance import Balance
from command.command_invoker import TransactionInvoker
from command.transaction_command import ApplyTransactionCommand
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class FailingCommand:
    def execute(self):
        raise ValueError("boom")

    def undo(self):
        raise AssertionError("should never be undone")


class TestTransactionCommand(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.invoker = TransactionInvoker()

    def _command(self, amount, category):
        return ApplyTransactionCommand(self.balance, Transaction(amount, category))

    def test_execute_applies_transaction(self):
        self.invoker.execute(self._command(100, TransactionCategory.INCOME))
        self.assertEqual(self.balance.get_balance(), Decimal("100"))
        self.assertEqual(len(self.invoker), 1)

    def test_undo_reverses_income_and_expense(self):
        self.invoker.execute(self._command(100, TransactionCategory.INCOME))
        self.invoker.execute(self._command("30.10", TransactionCategory.EXPENSE))
        self.assertEqual(self.balance.get_balance(), Decimal("69.90"))

        self.invoker.undo()
        self.assertEqual(self.balance.get_balance(), Decimal("100"))

        self.invoker.undo()
        self.assertEqual(self.balance.get_balance(), Decimal("0"))

    def test_undo_with_empty_history_returns_none(self):
        self.assertIsNone(self.invoker.undo())
        self.assertEqual(self.balance.get_balance(), Decimal("0"))

    def test_failed_command_is_not_recorded(self):
        with self.assertRaises(ValueError):
            self.invoker.execute(FailingCommand())
        self.assertEqual(len(self.invoker), 0)

    def test_invalid_category_is_rejected_and_not_recorded(self):
        class FakeCategory:
            pass

        with self.assertRaises(ValueError):
            self.invoker.execute(self._command(10, FakeCategory()))
        self.assertEqual(len(self.invoker), 0)

    def test_history_is_capped(self):
        invoker = TransactionInvoker(max_history=2)
        for _ in range(5):
            invoker.execute(self._command(1, TransactionCategory.INCOME))

        self.assertEqual(len(invoker), 2)
        invoker.undo()
        invoker.undo()
        self.assertIsNone(invoker.undo())
        self.assertEqual(self.balance.get_balance(), Decimal("3"))

    def test_rejects_invalid_max_history(self):
        for value in (0, -1, 1.5, True, "10"):
            with self.assertRaises(ValueError):
                TransactionInvoker(max_history=value)

    def test_clear_forgets_history(self):
        self.invoker.execute(self._command(10, TransactionCategory.INCOME))
        self.invoker.clear()
        self.assertIsNone(self.invoker.undo())
        self.assertEqual(self.balance.get_balance(), Decimal("10"))

    def test_concurrent_execute_and_undo_is_consistent(self):
        invoker = TransactionInvoker(max_history=10_000)
        workers = 8
        per_worker = 200

        def run():
            for _ in range(per_worker):
                invoker.execute(self._command("0.01", TransactionCategory.INCOME))

        threads = [threading.Thread(target=run) for _ in range(workers)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(self.balance.get_balance(), Decimal("16.00"))
        self.assertEqual(len(invoker), workers * per_worker)

        while invoker.undo() is not None:
            pass
        self.assertEqual(self.balance.get_balance(), Decimal("0"))


if __name__ == "__main__":
    unittest.main()
