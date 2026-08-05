import sqlite3
from typing import NamedTuple

from database.transaction_repository import (
    delete_transaction,
    get_transaction_by_id,
    get_transactions,
    insert_transaction,
    update_transaction,
    update_transaction_posting_status,
    restore_transaction,
)
from database.records import TransactionDetailRecord

from utils.transaction_payload import build_transaction_payload
from utils.transaction_posting import (
    POSTED_STATUS,
    TEMPORARY_STATUS,
    is_valid_posting_status,
)
from utils.transaction_validation import validate_transaction_form


class TransactionSaveResult(NamedTuple):
    success: bool
    message: str


class TransactionPostResult(NamedTuple):
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
    posting_status=POSTED_STATUS,
):
    if not is_valid_posting_status(posting_status):
        return TransactionSaveResult(
            False,
            "Please select a valid posting status.",
        )

    is_valid, message = validate_transaction_form(
        account_id=account_id,
        amount=amount,
        transaction_type=transaction_type,
        category_id=category_id,
    )

    if not is_valid:
        return TransactionSaveResult(False, message)

    try:
        payload = build_transaction_payload(
            account_id=account_id,
            amount=amount,
            category_id=category_id,
            date_label=date_label,
            time_label=time_label,
            notes_label=notes_label,
        )
    except ValueError:
        return TransactionSaveResult(
            False,
            "Please select a valid date and time.",
        )

    if transaction_id is None:
        return _create_transaction(payload, posting_status)

    return _update_transaction(
        payload,
        transaction_id,
        posting_status,
    )


def _create_transaction(payload, posting_status):
    try:
        created = insert_transaction(
            payload["account_id"],
            payload["amount_centavos"],
            payload["category_id"],
            payload["date_time"],
            payload["notes"],
            posting_status=posting_status,
        )
    except sqlite3.Error:
        created = False

    if posting_status == TEMPORARY_STATUS:
        if created:
            return TransactionSaveResult(
                True,
                "Temporary transaction saved.",
            )
        return TransactionSaveResult(
            False,
            "Temporary transaction could not be saved.",
        )

    if created:
        return TransactionSaveResult(
            True,
            "Transaction added successfully.",
        )

    return TransactionSaveResult(
        False,
        "Transaction could not be added.",
    )


def _update_transaction(payload, transaction_id, posting_status):
    try:
        existing_transaction = get_transaction_by_id(transaction_id)
    except sqlite3.Error:
        existing_transaction = None

    if existing_transaction is None:
        return TransactionSaveResult(
            False,
            "Transaction could not be updated.",
        )

    if posting_status != existing_transaction.posting_status:
        return TransactionSaveResult(
            False,
            "Transaction status can only be changed by posting it.",
        )

    try:
        updated = update_transaction(
            payload["account_id"],
            payload["amount_centavos"],
            payload["category_id"],
            payload["date_time"],
            payload["notes"],
            transaction_id,
        )
    except sqlite3.Error:
        updated = False

    is_temporary = (
        existing_transaction.posting_status == TEMPORARY_STATUS
    )

    if not updated:
        return TransactionSaveResult(
            False,
            (
                "Temporary transaction could not be updated."
                if is_temporary
                else "Transaction could not be updated."
            ),
        )

    return TransactionSaveResult(
        True,
        (
            "Temporary transaction updated successfully."
            if is_temporary
            else "Transaction updated successfully."
        ),
    )


def get_empty_transaction_state(
    transaction_type=None,
    compact=False,
    account_filtered=False,
    advanced_filters_active=False,
):
    if advanced_filters_active:
        return {
            "title": "No matching transactions",
            "message": (
                "Try changing or resetting your search and filters."
            ),
        }

    if transaction_type == "income":
        return {
            "title": "No income transactions",
            "message": (
                "No income transactions match the current view."
            ),
        }

    if transaction_type == "expense":
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


def get_transactions_for_view(
    account_id=None,
    transaction_type=None,
    search_text=None,
    group_id=None,
    category_id=None,
    start_date=None,
    end_date=None,
    limit=None,
):
    return get_transactions(
        account_id=account_id,
        transaction_type=transaction_type,
        search_text=search_text,
        group_id=group_id,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )


def get_transaction_list_data(
    account_id=None,
    transaction_type=None,
    search_text=None,
    group_id=None,
    category_id=None,
    start_date=None,
    end_date=None,
    limit=None,
    compact_empty_state=False,
):
    transactions = get_transactions_for_view(
        account_id=account_id,
        transaction_type=transaction_type,
        search_text=search_text,
        group_id=group_id,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    advanced_filters_active = any(
        (
            search_text,
            group_id is not None,
            category_id is not None,
            start_date is not None,
            end_date is not None,
        )
    )

    empty_state = get_empty_transaction_state(
        transaction_type,
        compact_empty_state,
        account_filtered=account_id is not None,
        advanced_filters_active=advanced_filters_active,
    )

    return {
        "transactions": transactions,
        "empty_state": empty_state,
    }


def get_transaction_for_edit(transaction_id):
    return get_transaction_by_id(transaction_id)


def post_transaction_by_id(transaction_id):
    try:
        transaction = get_transaction_by_id(transaction_id)
    except sqlite3.Error:
        transaction = None

    if transaction is None:
        return TransactionPostResult(
            False,
            "Transaction could not be posted.",
        )

    if transaction.posting_status == POSTED_STATUS:
        return TransactionPostResult(
            False,
            "Transaction is already posted.",
        )

    try:
        posted = update_transaction_posting_status(
            transaction_id,
            POSTED_STATUS,
            expected_posting_status=TEMPORARY_STATUS,
        )
    except sqlite3.Error:
        posted = False

    if posted:
        return TransactionPostResult(
            True,
            "Temporary transaction posted.",
        )

    return TransactionPostResult(
        False,
        "Temporary transaction could not be posted.",
    )


def delete_transaction_by_id(transaction_id):
    try:
        transaction = get_transaction_by_id(transaction_id)
    except sqlite3.Error:
        transaction = None

    if transaction is None:
        return TransactionDeleteResult(
            False,
            "Transaction could not be deleted.",
        )

    try:
        deleted = delete_transaction(transaction_id)
    except sqlite3.Error:
        deleted = False

    is_temporary = transaction.posting_status == TEMPORARY_STATUS

    if deleted:
        return TransactionDeleteResult(
            True,
            (
                "Temporary transaction deleted."
                if is_temporary
                else "Transaction deleted."
            ),
            transaction,
        )

    return TransactionDeleteResult(
        False,
        (
            "Temporary transaction could not be deleted."
            if is_temporary
            else "Transaction could not be deleted."
        ),
    )


def restore_deleted_transaction(transaction):
    try:
        restored = restore_transaction(transaction)
    except sqlite3.Error:
        restored = False

    is_temporary = transaction.posting_status == TEMPORARY_STATUS

    if restored:
        return TransactionRestoreResult(
            True,
            (
                "Temporary transaction restored."
                if is_temporary
                else "Transaction restored."
            ),
        )

    return TransactionRestoreResult(
        False,
        (
            "Temporary transaction could not be restored."
            if is_temporary
            else "Transaction could not be restored."
        ),
    )
