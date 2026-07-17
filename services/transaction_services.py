from database.transaction_repository import delete_transaction, get_transactions

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

def get_transaction_list_data(
    account_id=None,
    transaction_filter=None,
    limit=None,
    compact_empty_state=False,
):
    transactions = get_transactions_for_view(
        account_id=account_id,
        transaction_filter=transaction_filter,
        limit=limit
    )

    empty_state = get_empty_transaction_state(
        transaction_filter,
        compact_empty_state
    )

    return {
        "transactions": transactions,
        "empty_state": empty_state,
    }

def delete_transaction_by_id(transaction_id):
    return delete_transaction(transaction_id)
