from database.transaction_repository import delete_transaction, get_transactions

from widgets.transaction_list import render_transaction_list

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
    account_id = getattr(screen, "selected_account_id", None)

    transactions = get_transactions_for_view(
        account_id=account_id,
        transaction_filter=screen.transaction_filter,
        limit=limit
    )

    empty_state = get_empty_transaction_state(
        screen.transaction_filter,
        compact_empty_state
    )

    render_transaction_list(
        container=screen.ids.transactions_container,
        transactions=transactions,
        screen=screen,
        empty_state=empty_state,
    )

def delete_transaction_by_id(transaction_id):
    delete_transaction(transaction_id)