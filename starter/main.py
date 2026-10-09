"""This module serves as the entry point for the program."""
from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver
from balance.balance_observer import PrintBalance
from command.command_invoker import TransactionInvoker
from command.transaction_command import ApplyTransactionCommand
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from transaction.transaction_adapter import TransactionAdapter
from transaction.external_income_transaction import ExternalFreelanceIncome


def main():
    print("Adding transactions...")

    balance = Balance.get_instance()
    # Keep strong references: Balance holds observers weakly.
    print_observer = PrintBalance()
    low_balance_observer = LowBalanceAlertObserver(threshold=100)
    balance.register_observer(print_observer)
    balance.register_observer(low_balance_observer)

    # Create standard transactions
    transactions = [
        Transaction(100, TransactionCategory.INCOME),
        Transaction(50, TransactionCategory.EXPENSE),
        Transaction(200, TransactionCategory.INCOME),
        Transaction(75, TransactionCategory.EXPENSE),
    ]

    # Create an external income transaction (via Adapter pattern)
    freelance_income = ExternalFreelanceIncome(
        1200, "INV-98765", "Mobile App Project")
    adapter = TransactionAdapter(freelance_income)
    adapted_transaction = adapter.to_transaction()

    all_transactions = transactions + [adapted_transaction]

    invoker = TransactionInvoker()
    for transaction in all_transactions:
        invoker.execute(ApplyTransactionCommand(balance, transaction))

    print(balance.summary())

    print("Undoing last transaction...")
    invoker.undo()
    print(balance.summary())


if __name__ == "__main__":
    main()
