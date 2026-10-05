import threading
import weakref
from decimal import Decimal
from decimal import InvalidOperation

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class Balance:
    """Singleton to track the balance."""

    _instance = None
    _instance_lock = threading.Lock()

    def __init__(self):
        """Initialize the balance. Prevent direct instantiation."""
        if Balance._instance is not None:
            raise RuntimeError("Use Balance.get_instance() to access the singleton.")

        self._net_balance = Decimal("0")
        self._observers = weakref.WeakSet()
        self._state_lock = threading.RLock()

    @classmethod
    def get_instance(cls):
        """Return the single shared Balance instance."""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @staticmethod
    def _validate_amount(amount):
        """Return amount as a finite Decimal."""
        try:
            value = Decimal(str(amount))
        except (TypeError, ValueError, InvalidOperation) as exc:
            raise ValueError("Amount must be numeric") from exc

        if not value.is_finite():
            raise ValueError("Amount must be finite")

        return value

    def reset(self):
        """Reset the net balance to zero."""
        with self._state_lock:
            self._net_balance = Decimal("0")
            self._observers.clear()

    def add_income(self, amount):
        """Add income to the balance."""
        self.apply_transaction(Transaction(amount, TransactionCategory.INCOME))

    def add_expense(self, amount):
        """Subtract expense from the balance."""
        self.apply_transaction(Transaction(amount, TransactionCategory.EXPENSE))

    def register_observer(self, observer):
        """Register an observer for balance updates."""
        if not hasattr(observer, "update") or not callable(observer.update):
            raise ValueError("Observer must define an update(balance, transaction) method")

        with self._state_lock:
            self._observers.add(observer)

    def unregister_observer(self, observer):
        """Unregister an observer if present."""
        with self._state_lock:
            self._observers.discard(observer)

    def notify_observers(self, transaction, current_balance):
        """Notify all observers after a transaction is applied."""
        with self._state_lock:
            for observer in tuple(self._observers):
                observer.update(current_balance, transaction)

    def apply_transaction(self, transaction):
        """Apply a transaction and notify observers with the updated balance."""
        amount = self._validate_amount(transaction.amount)

        with self._state_lock:
            if transaction.category == TransactionCategory.INCOME:
                self._net_balance += amount
            elif transaction.category == TransactionCategory.EXPENSE:
                self._net_balance -= amount
            else:
                raise ValueError("Invalid transaction category")

            # Notify under the lock so observers see updates in order.
            self.notify_observers(transaction, self._net_balance)

    def get_balance(self):
        """Get the current net balance."""
        with self._state_lock:
            return self._net_balance

    def summary(self):
        """Return a summary string of the net balance."""
        with self._state_lock:
            return f"Current balance: ${self._net_balance:.2f}"
    
