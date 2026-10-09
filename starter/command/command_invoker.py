import threading
from collections import deque


class TransactionInvoker:
    """Runs commands and keeps a capped history so they can be undone."""

    def __init__(self, max_history=100):
        if (
            not isinstance(max_history, int)
            or isinstance(max_history, bool)
            or max_history < 1
        ):
            raise ValueError("max_history must be a positive integer")

        # Oldest commands are dropped once full, so memory use stays capped.
        self._history = deque(maxlen=max_history)
        self._lock = threading.Lock()

    def execute(self, command):
        """Run a command and record it only if it succeeds."""
        with self._lock:
            command.execute()
            self._history.append(command)

    def undo(self):
        """Undo the latest command, or return None if history is empty."""
        with self._lock:
            if not self._history:
                return None

            command = self._history.pop()
            try:
                command.undo()
            except Exception:
                self._history.append(command)
                raise

            return command

    def clear(self):
        """Forget all recorded commands."""
        with self._lock:
            self._history.clear()

    def __len__(self):
        with self._lock:
            return len(self._history)
