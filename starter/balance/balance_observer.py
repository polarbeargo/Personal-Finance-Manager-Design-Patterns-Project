# balance_observer.py


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
        self.threshold = float(threshold)
        self.alert_triggered = False

    def update(self, balance, transaction):
        """Alert if balance drops below threshold."""
        self.alert_triggered = balance < self.threshold
