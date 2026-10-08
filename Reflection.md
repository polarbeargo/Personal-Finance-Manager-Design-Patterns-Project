# Design Reflection

This project uses four patterns to keep balance management, transaction conversion, change notifications, and undo behavior in distinct parts of the application.

## Singleton: shared balance manager
`Balance.get_instance()` provides one shared balance manager. This keeps the application’s balance state consistent and gives transactions and observers a common point of coordination. A lock protects first-time instance creation, and another protects state access.

**Trade-off:** global shared state can make tests and future multiple-account support harder. Tests must reset the singleton between cases; a multi-account version would likely use separate balance instances rather than a process-wide singleton.

## Observer: balance-change notifications
`Balance` notifies registered `PrintObserver` and `LowBalanceAlertObserver` instances when transactions change the balance. This separates reporting and alert rules from the balance calculation, making observers independently replaceable and testable. Weak references avoid the balance manager keeping otherwise-unused observers alive.

**Trade-off:** callers must keep strong references to observers while they are needed. Notifications are synchronized with balance updates to preserve order, so a slow observer can delay other balance operations.

## Adapter: external freelance income
`TransactionAdapter` translates the freelance platform’s income object into the application’s `Transaction` format. The balance manager can therefore process external income through the same path as native transactions, without depending on the external object’s shape.

**Trade-off:** the internal `Transaction` currently stores only amount and category. Invoice ID and project description are checked on the external object but are not retained in the converted transaction, so richer reporting would require extending the internal model.

## Command: undoable transactions
### Why the Command pattern
A finance app needs to fix mistakes. Before this change, applying a transaction was a direct call to `Balance.apply_transaction()`, so nothing recorded what happened and nothing could be reversed. The Command pattern turns each transaction into an object that knows how to run itself and how to undo itself. That adds undo support without adding history logic to `Balance`, `Transaction`, or the observers.

I considered Strategy (for example, swappable alert rules) and Decorator (for example, adding fees to transactions). Neither addresses the current app's need to reverse a transaction as directly as Command does.

### Where it fits
- `command/transaction_command.py` defines `Command` with `execute()` and `undo()`. `ApplyTransactionCommand` holds a balance and transaction; undo applies the opposite category.
- `command/command_invoker.py` defines `TransactionInvoker`, which runs commands and keeps a bounded history.
- `main.py` sends each native or adapted transaction through the invoker and demonstrates undoing the last one.

The flow is `main.py` → `TransactionInvoker` → `ApplyTransactionCommand` → `Balance` (Singleton) → observers. Undo also goes through `Balance.apply_transaction()`, so observers receive the reversal.

### How it improves flexibility, testability, and scalability
- **Flexibility:** new actions can be added as separate `Command` subclasses without changing the invoker or balance manager.
- **Testability:** commands and the invoker can be tested independently. The tests include a failing fake command to verify failed actions are not recorded.
- **Scalability:** the fixed-size history bounds memory use, while the invoker's lock protects command order when shared across threads.

### Quality properties
- **Thread safety:** the invoker serializes execution and undo, and the balance protects its own state. The lock order is invoker then balance; the balance does not call back into the invoker.
- **Reliability:** only successful commands are recorded. If undo fails, the command is restored to history.
- **Accuracy:** undo reuses the original `Decimal` amount and reverses its category.
- **Memory:** the history uses a capped `deque`; command instances are frozen, slot-backed dataclasses.
- **Speed:** execute, append, and pop are constant-time operations.

`command/test_transaction_command.py` covers execution, undo for income and expense, empty history, failed commands, invalid categories, the history cap, invalid limits, clearing history, and concurrent execution/undo.

**Trade-off:** undo applies the opposite income or expense, which works for this single-balance model but would need a richer reversal strategy for transfers, fees, or other multi-step operations. Because history is capped, older commands eventually cannot be undone.

## Overall
The patterns improve separation of concerns and make each behavior easier to test or extend. They also add some machinery: shared singleton state, observer lifecycle/ordering concerns, an adapter boundary, and command history. For this small application, those costs are acceptable because they directly support the project’s required behaviors; a larger system would need explicit account scoping, durable transaction history, and richer transaction metadata.
