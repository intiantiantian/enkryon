from typing import NamedTuple

from database.transaction_repository import (
    delete_transaction,
    get_transaction_by_id,
    get_transactions,
    insert_transaction,
    update_transaction,
    restore_transaction,
)
from database.records import TransactionDetailRecord

from utils.transaction_payload import build_transaction_payload
from utils.transaction_validation import validate_transaction_form


class TransactionSaveResult(NamedTuple):
    success: bool
    message: str


class TransactionDeleteResult(NamedTuple):
    success: bool
    message: str
    deleted_transaction: TransactionDetailRecord | None = None


class TransactionRestoreResult(NamedTuple):
    success: bool
    message: str


def save_transaction(
    *,
    account_id,
    amount,
    transaction_type,
    category_id,
    date_label,
    time_label,
    notes_label,
    transaction_id=None,
):
    is_valid, message = validate_transaction_form(
        account_id=account_id,
        amount=amount,
        transaction_type=transaction_type,
        category_id=category_id,
    )

    if not is_valid:
        return TransactionSaveResult(False, message)

    payload = build_transaction_payload(
        account_id=account_id,
        amount=amount,
        category_id=category_id,
        date_label=date_label,
        time_label=time_label,
        notes_label=notes_label,
    )

    if transaction_id is None:
        created = insert_transaction(
            payload["account_id"],
            payload["amount_centavos"],
            payload["category_id"],
            payload["date_time"],
            payload["notes"],
        )

        if not created:
            return TransactionSaveResult(
                False,
                "Transaction could not be added.",
            )

        return TransactionSaveResult(
            True,
            "Transaction added successfully.",
        )

    updated = update_transaction(
        payload["account_id"],
        payload["amount_centavos"],
        payload["category_id"],
        payload["date_time"],
        payload["notes"],
        transaction_id,
    )

    if not updated:
        return TransactionSaveResult(
            False,
            "Transaction could not be updated.",
        )

    return TransactionSaveResult(
        True,
        "Transaction updated successfully.",
    )


def get_empty_transaction_state(
    transaction_filter=None,
    compact=False,
    account_filtered=False,
):
    if transaction_filter == "income":
        return {
            "title": "No income transactions",
            "message": (
                "No income transactions match the current view."
            ),
        }

    if transaction_filter == "expense":
        return {
            "title": "No expense transactions",
            "message": (
                "No expense transactions match the current view."
            ),
        }

    if account_filtered:
        return {
            "title": "No transactions for this account",
            "message": (
                "This account does not have any transactions yet."
            ),
        }

    if compact:
        return {
            "title": "No transactions yet",
            "message": (
                "Add a transaction to start tracking your money."
            ),
        }

    return {
        "title": "No transactions yet",
        "message": (
            "Add a transaction to start building your history."
        ),
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
        compact_empty_state,
        account_filtered=account_id is not None,
    )

    return {
        "transactions": transactions,
        "empty_state": empty_state,
    }


def get_transaction_for_edit(transaction_id):
    return get_transaction_by_id(transaction_id)


def delete_transaction_by_id(transaction_id):
    transaction = get_transaction_by_id(transaction_id)

    if transaction is None:
        return TransactionDeleteResult(
            False,
            "Transaction could not be deleted.",
        )

    deleted = delete_transaction(transaction_id)

    if deleted:
        return TransactionDeleteResult(
            True,
            "Transaction deleted.",
            transaction,
        )

    return TransactionDeleteResult(
        False,
        "Transaction could not be deleted.",
    )


def restore_deleted_transaction(transaction):
    restored = restore_transaction(transaction)

    if restored:
        return TransactionRestoreResult(
            True,
            "Transaction restored.",
        )

    return TransactionRestoreResult(
        False,
        "Transaction could not be restored.",
    )
