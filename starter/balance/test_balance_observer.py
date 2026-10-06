import io
import unittest
from contextlib import redirect_stdout

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver
from balance.balance_observer import PrintObserver

class TestLowBalanceAlertObserver(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_alert_triggers_on_low_balance(self):
        observer = LowBalanceAlertObserver(threshold=50)
        self.balance.register_observer(observer)

        self.balance.apply_transaction(Transaction(100, TransactionCategory.INCOME))
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(60, TransactionCategory.EXPENSE))
        self.assertTrue(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(100, TransactionCategory.INCOME))
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(60, TransactionCategory.EXPENSE))
        self.assertFalse(observer.alert_triggered)
        
        self.balance.apply_transaction(Transaction(60, TransactionCategory.EXPENSE))
        self.assertTrue(observer.alert_triggered)

    def test_alert_prints_once_per_drop(self):
        observer = LowBalanceAlertObserver(threshold=50)
        self.balance.register_observer(observer)

        output = io.StringIO()
        with redirect_stdout(output):
            self.balance.add_expense(10)
            self.balance.add_expense(10)

        self.assertEqual(output.getvalue().count("ALERT"), 1)

    def test_add_income_and_expense_notify_observers(self):
        observer = LowBalanceAlertObserver(threshold=50)
        self.balance.register_observer(observer)

        self.balance.add_income(100)
        self.assertFalse(observer.alert_triggered)

        with redirect_stdout(io.StringIO()):
            self.balance.add_expense(60)
        self.assertTrue(observer.alert_triggered)


class TestPrintObserver(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_prints_on_every_balance_change(self):
        observer = PrintObserver()
        self.balance.register_observer(observer)

        output = io.StringIO()
        with redirect_stdout(output):
            self.balance.apply_transaction(Transaction(100, TransactionCategory.INCOME))
            self.balance.apply_transaction(Transaction(40, TransactionCategory.EXPENSE))

        lines = output.getvalue().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("Updated balance: $100.00", lines[0])
        self.assertIn("Updated balance: $60.00", lines[1])

    def test_unregistered_observer_is_not_notified(self):
        observer = PrintObserver()
        self.balance.register_observer(observer)
        self.balance.unregister_observer(observer)

        output = io.StringIO()
        with redirect_stdout(output):
            self.balance.add_income(10)

        self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
