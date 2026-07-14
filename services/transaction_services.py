from database.transaction_repository import delete_transaction, get_transactions

from utils.snackbar import show_snackbar

from widgets.transaction_card import TransactionCard, create_transaction_empty_state

def get_empty_transaction_state(transaction_filter=None, compact=False):
    if transaction_filter == "income":
        return {
            "title": "No income transactions found",
            "message": "Income transactions will appear here."
        }

    if transaction_filter == "expense":
        return {
            "title": "No expense transactions found",
            "message": "Expense transactions will appear here."
        }

    if compact:
        return {
            "title": "No transactions yet",
            "message": "Tap + Add Transaction to create your first transaction."
        }

    return {
        "title": "No transactions yet",
        "message": "Go back to Dashboard and tap + Add Transaction."
    }

def get_transactions_for_view(account_id=None, transaction_filter=None, limit=None):
    return get_transactions(
        account_id=account_id,
        transaction_type=transaction_filter,
        limit=limit
    )

def load_transactions(screen, limit=None, compact_empty_state=False):
    screen.ids.transactions_container.clear_widgets()

    account_id = getattr(screen, "selected_account_id", None)

    transactions = get_transactions_for_view(
        account_id=account_id,
        transaction_filter=screen.transaction_filter,
        limit=limit
    )

    if not transactions:
        empty_state = get_empty_transaction_state(
            screen.transaction_filter,
            compact=compact_empty_state
        )

        screen.ids.transactions_container.add_widget(
            create_transaction_empty_state(empty_state)
        )
        return

    for transaction in transactions:
        card = TransactionCard()
        card.screen = screen
        card.set_transaction(transaction)
        screen.ids.transactions_container.add_widget(card)

def perform_delete_transaction(self, transaction_id, dialog_screen):
    delete_transaction(transaction_id)
    close_delete_transaction_dialog(dialog_screen)
    self.load_dashboard()
    show_snackbar("Transaction deleted successfully.")

def close_delete_transaction_dialog(dialog_screen):
    dialog_screen.dismiss()