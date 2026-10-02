# balance_observer.py

from decimal import Decimal
from decimal import InvalidOperation


class IBalanceObserver:
    """Interface for balance observers."""

    def update(self, balance, transaction):
        """Handle balance updates."""
        raise NotImplementedError("Subclasses must implement update method.")


class PrintObserver(IBalanceObserver):
    """Observer that logs balance changes to stdout."""

    def update(self, balance, transaction):
        """Print balance update message."""
        print(
            f"Transaction applied: {transaction}. "
            f"Updated balance: ${balance:.2f}"
        )


class LowBalanceAlertObserver(IBalanceObserver):
    """Observer that flags when balance drops below a threshold."""

    def __init__(self, threshold):
        try:
            self.threshold = Decimal(str(threshold))
        except (TypeError, ValueError, InvalidOperation) as exc:
            raise ValueError("Threshold must be numeric") from exc

        if not self.threshold.is_finite():
            raise ValueError("Threshold must be finite")

        self.alert_triggered = False

    def update(self, balance, transaction):
        """Alert if balance drops below threshold."""
        self.alert_triggered = balance < self.threshold
