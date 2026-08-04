import sqlite3
from typing import NamedTuple

from database.account_repository import get_account_by_id
from database.records import TransferRecord
from database.transfer_repository import (
    delete_transfer,
    get_transfer_by_id,
    insert_transfer,
    restore_transfer,
    update_transfer,
)
from utils.money import pesos_to_centavos
from utils.transaction_datetime import combine_date_time_labels
from utils.transaction_payload import normalize_transaction_notes


class TransferSaveResult(NamedTuple):
    success: bool
    message: str


class TransferDeleteResult(NamedTuple):
    success: bool
    message: str
    deleted_transfer: TransferRecord | None = None


class TransferRestoreResult(NamedTuple):
    success: bool
    message: str


def validate_transfer_form(
    source_account_id,
    destination_account_id,
    amount,
):
    if source_account_id is None:
        return False, "Please select a source account."

    if destination_account_id is None:
        return False, "Please select a destination account."

    if source_account_id == destination_account_id:
        return (
            False,
            "Source and destination accounts must be different.",
        )

    try:
        amount_centavos = pesos_to_centavos(amount)
    except (ValueError, OverflowError):
        return (
            False,
            "Please enter a valid amount with up to two decimal places.",
        )

    if amount_centavos <= 0:
        return False, "Amount cannot be less than or equal to zero."

    return True, None


def build_transfer_payload(
    source_account_id,
    destination_account_id,
    amount,
    date_label,
    time_label,
    notes_label,
):
    return {
        "source_account_id": source_account_id,
        "destination_account_id": destination_account_id,
        "amount_centavos": pesos_to_centavos(amount),
        "date_time": combine_date_time_labels(date_label, time_label),
        "notes": normalize_transaction_notes(notes_label or ""),
    }


def save_transfer(
    *,
    source_account_id,
    destination_account_id,
    amount,
    date_label,
    time_label,
    notes_label,
    transfer_id=None,
):
    is_valid, message = validate_transfer_form(
        source_account_id,
        destination_account_id,
        amount,
    )

    if not is_valid:
        return TransferSaveResult(False, message)

    try:
        payload = build_transfer_payload(
            source_account_id,
            destination_account_id,
            amount,
            date_label,
            time_label,
            notes_label,
        )
    except ValueError:
        return TransferSaveResult(
            False,
            "Please select a valid date and time.",
        )

    account_error = _get_account_error(
        source_account_id,
        destination_account_id,
    )
    if account_error is not None:
        return TransferSaveResult(False, account_error)

    is_create = transfer_id is None

    try:
        if is_create:
            saved = insert_transfer(
                payload["source_account_id"],
                payload["destination_account_id"],
                payload["amount_centavos"],
                payload["date_time"],
                payload["notes"],
            )
        else:
            saved = update_transfer(
                payload["source_account_id"],
                payload["destination_account_id"],
                payload["amount_centavos"],
                payload["date_time"],
                payload["notes"],
                transfer_id,
            )
    except sqlite3.Error:
        saved = False

    if not saved:
        action = "added" if is_create else "updated"
        return TransferSaveResult(
            False,
            f"Transfer could not be {action}.",
        )

    action = "added" if is_create else "updated"
    return TransferSaveResult(
        True,
        f"Transfer {action} successfully.",
    )


def get_transfer_for_edit(transfer_id):
    return get_transfer_by_id(transfer_id)


def delete_transfer_by_id(transfer_id):
    try:
        transfer = get_transfer_by_id(transfer_id)
    except sqlite3.Error:
        transfer = None

    if transfer is None:
        return TransferDeleteResult(
            False,
            "Transfer could not be deleted.",
        )

    try:
        deleted = delete_transfer(transfer_id)
    except sqlite3.Error:
        deleted = False

    if not deleted:
        return TransferDeleteResult(
            False,
            "Transfer could not be deleted.",
        )

    return TransferDeleteResult(
        True,
        "Transfer deleted.",
        transfer,
    )


def restore_deleted_transfer(transfer):
    account_error = _get_account_error(
        transfer.source_account_id,
        transfer.destination_account_id,
    )
    if account_error is not None:
        return TransferRestoreResult(False, account_error)

    try:
        restored = restore_transfer(transfer)
    except sqlite3.Error:
        restored = False

    if not restored:
        return TransferRestoreResult(
            False,
            "Transfer could not be restored.",
        )

    return TransferRestoreResult(
        True,
        "Transfer restored.",
    )


def _get_account_error(source_account_id, destination_account_id):
    try:
        source_account = get_account_by_id(source_account_id)
        if source_account is None:
            return "Source account no longer exists."

        destination_account = get_account_by_id(destination_account_id)
        if destination_account is None:
            return "Destination account no longer exists."
    except sqlite3.Error:
        return "Accounts could not be verified."

    return None
