import sqlite3
from unittest.mock import Mock

import pytest

from services import transaction_services


def make_arguments(**overrides):
    arguments = {
        "account_id": 2,
        "amount": "123.45",
        "transaction_type": "expense",
        "category_id": 8,
        "date_label": "2026-08-05",
        "time_label": "07:30 PM",
        "notes_label": "Dinner",
    }
    arguments.update(overrides)
    return arguments


def make_transaction(posting_status="temporary"):
    return transaction_services.TransactionDetailRecord(
        transaction_id=17,
        account_id=2,
        amount_centavos=12345,
        category_id=8,
        date_time="2026-08-05 19:30:00",
        notes="Dinner",
        account_name="Cash",
        category_name="Dining",
        group_id=5,
        group_name="Food",
        transaction_type="expense",
        posting_status=posting_status,
    )


@pytest.mark.parametrize(
    ("repository_result", "success", "message"),
    [
        (True, True, "Temporary transaction saved."),
        (False, False, "Temporary transaction could not be saved."),
    ],
)
def test_save_temporary_transaction_uses_explicit_status(
    monkeypatch,
    repository_result,
    success,
    message,
):
    insert_transaction = Mock(return_value=repository_result)
    monkeypatch.setattr(
        transaction_services,
        "insert_transaction",
        insert_transaction,
    )

    result = transaction_services.save_transaction(
        **make_arguments(posting_status="temporary")
    )

    assert result == transaction_services.TransactionSaveResult(
        success,
        message,
    )
    insert_transaction.assert_called_once_with(
        2,
        12345,
        8,
        "2026-08-05 19:30:00",
        "Dinner",
        posting_status="temporary",
    )


def test_save_transaction_rejects_unknown_posting_status_before_validation(
    monkeypatch,
):
    validate_transaction_form = Mock()
    insert_transaction = Mock()
    monkeypatch.setattr(
        transaction_services,
        "validate_transaction_form",
        validate_transaction_form,
    )
    monkeypatch.setattr(
        transaction_services,
        "insert_transaction",
        insert_transaction,
    )

    result = transaction_services.save_transaction(
        **make_arguments(posting_status="pending")
    )

    assert result == transaction_services.TransactionSaveResult(
        False,
        "Please select a valid posting status.",
    )
    validate_transaction_form.assert_not_called()
    insert_transaction.assert_not_called()


def test_save_transaction_rejects_invalid_date_before_repository_access(
    monkeypatch,
):
    insert_transaction = Mock()
    monkeypatch.setattr(
        transaction_services,
        "insert_transaction",
        insert_transaction,
    )

    result = transaction_services.save_transaction(
        **make_arguments(date_label="not a date")
    )

    assert result == transaction_services.TransactionSaveResult(
        False,
        "Please select a valid date and time.",
    )
    insert_transaction.assert_not_called()


def test_create_handles_repository_exception(monkeypatch):
    monkeypatch.setattr(
        transaction_services,
        "insert_transaction",
        Mock(side_effect=sqlite3.OperationalError),
    )

    result = transaction_services.save_transaction(
        **make_arguments(posting_status="temporary")
    )

    assert result == transaction_services.TransactionSaveResult(
        False,
        "Temporary transaction could not be saved.",
    )


@pytest.mark.parametrize(
    ("repository_result", "success", "message"),
    [
        (True, True, "Temporary transaction updated successfully."),
        (False, False, "Temporary transaction could not be updated."),
    ],
)
def test_edit_temporary_transaction_preserves_status(
    monkeypatch,
    repository_result,
    success,
    message,
):
    get_transaction_by_id = Mock(
        return_value=make_transaction("temporary")
    )
    update_transaction = Mock(return_value=repository_result)
    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        get_transaction_by_id,
    )
    monkeypatch.setattr(
        transaction_services,
        "update_transaction",
        update_transaction,
    )

    result = transaction_services.save_transaction(
        **make_arguments(
            transaction_id=17,
            posting_status="temporary",
        )
    )

    assert result == transaction_services.TransactionSaveResult(
        success,
        message,
    )
    get_transaction_by_id.assert_called_once_with(17)
    update_transaction.assert_called_once_with(
        2,
        12345,
        8,
        "2026-08-05 19:30:00",
        "Dinner",
        17,
    )


def test_edit_rejects_posting_status_change(monkeypatch):
    update_transaction = Mock()
    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        Mock(return_value=make_transaction("temporary")),
    )
    monkeypatch.setattr(
        transaction_services,
        "update_transaction",
        update_transaction,
    )

    result = transaction_services.save_transaction(
        **make_arguments(
            transaction_id=17,
            posting_status="posted",
        )
    )

    assert result == transaction_services.TransactionSaveResult(
        False,
        "Transaction status can only be changed by posting it.",
    )
    update_transaction.assert_not_called()


@pytest.mark.parametrize(
    "repository_value",
    [None, sqlite3.OperationalError("database unavailable")],
)
def test_edit_handles_missing_record_or_lookup_failure(
    monkeypatch,
    repository_value,
):
    if isinstance(repository_value, Exception):
        get_transaction_by_id = Mock(side_effect=repository_value)
    else:
        get_transaction_by_id = Mock(return_value=repository_value)
    update_transaction = Mock()
    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        get_transaction_by_id,
    )
    monkeypatch.setattr(
        transaction_services,
        "update_transaction",
        update_transaction,
    )

    result = transaction_services.save_transaction(
        **make_arguments(
            transaction_id=17,
            posting_status="temporary",
        )
    )

    assert result == transaction_services.TransactionSaveResult(
        False,
        "Transaction could not be updated.",
    )
    update_transaction.assert_not_called()


def test_edit_handles_repository_exception(monkeypatch):
    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        Mock(return_value=make_transaction("temporary")),
    )
    monkeypatch.setattr(
        transaction_services,
        "update_transaction",
        Mock(side_effect=sqlite3.OperationalError),
    )

    result = transaction_services.save_transaction(
        **make_arguments(
            transaction_id=17,
            posting_status="temporary",
        )
    )

    assert result == transaction_services.TransactionSaveResult(
        False,
        "Temporary transaction could not be updated.",
    )
