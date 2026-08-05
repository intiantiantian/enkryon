import sqlite3
from unittest.mock import Mock

import pytest

from database import transaction_repository
from database.account_repository import insert_account
from database.category_group_repository import insert_category_group
from database.category_repository import insert_category
from database.transaction_repository import (
    get_current_balance_centavos,
    get_total_centavos,
    get_transaction_by_id,
    insert_transaction,
)
from services import transaction_services


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


def seed_temporary_expense(amount_centavos=12345):
    assert insert_account("Cash") is True
    assert insert_category_group("Food", "expense") == (True, None)
    assert insert_category(1, "Dining") == (True, None)
    assert insert_transaction(
        1,
        amount_centavos,
        1,
        "2026-08-05 19:30:00",
        "Dinner",
        posting_status="temporary",
    ) is True


def test_post_transaction_uses_compare_and_set(monkeypatch):
    get_transaction_by_id = Mock(return_value=make_transaction())
    update_status = Mock(return_value=True)
    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        get_transaction_by_id,
    )
    monkeypatch.setattr(
        transaction_services,
        "update_transaction_posting_status",
        update_status,
    )

    result = transaction_services.post_transaction_by_id(17)

    assert result == transaction_services.TransactionPostResult(
        True,
        "Temporary transaction posted.",
    )
    get_transaction_by_id.assert_called_once_with(17)
    update_status.assert_called_once_with(
        17,
        "posted",
        expected_posting_status="temporary",
    )


def test_post_transaction_rejects_already_posted_record(monkeypatch):
    update_status = Mock()
    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        Mock(return_value=make_transaction("posted")),
    )
    monkeypatch.setattr(
        transaction_services,
        "update_transaction_posting_status",
        update_status,
    )

    result = transaction_services.post_transaction_by_id(17)

    assert result == transaction_services.TransactionPostResult(
        False,
        "Transaction is already posted.",
    )
    update_status.assert_not_called()


@pytest.mark.parametrize(
    "repository_value",
    [None, sqlite3.OperationalError("database unavailable")],
)
def test_post_transaction_handles_missing_record_or_lookup_failure(
    monkeypatch,
    repository_value,
):
    if isinstance(repository_value, Exception):
        get_transaction_by_id = Mock(side_effect=repository_value)
    else:
        get_transaction_by_id = Mock(return_value=repository_value)
    update_status = Mock()
    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        get_transaction_by_id,
    )
    monkeypatch.setattr(
        transaction_services,
        "update_transaction_posting_status",
        update_status,
    )

    result = transaction_services.post_transaction_by_id(17)

    assert result == transaction_services.TransactionPostResult(
        False,
        "Transaction could not be posted.",
    )
    update_status.assert_not_called()


@pytest.mark.parametrize(
    "repository_value",
    [False, sqlite3.OperationalError("database unavailable")],
)
def test_post_transaction_handles_compare_and_set_failure(
    monkeypatch,
    repository_value,
):
    if isinstance(repository_value, Exception):
        update_status = Mock(side_effect=repository_value)
    else:
        update_status = Mock(return_value=repository_value)
    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        Mock(return_value=make_transaction()),
    )
    monkeypatch.setattr(
        transaction_services,
        "update_transaction_posting_status",
        update_status,
    )

    result = transaction_services.post_transaction_by_id(17)

    assert result == transaction_services.TransactionPostResult(
        False,
        "Temporary transaction could not be posted.",
    )


def test_post_transaction_updates_exact_totals_once():
    seed_temporary_expense(12345)

    assert get_total_centavos("expense") == 0
    assert get_current_balance_centavos() == 0

    first_result = transaction_services.post_transaction_by_id(1)
    second_result = transaction_services.post_transaction_by_id(1)

    assert first_result == transaction_services.TransactionPostResult(
        True,
        "Temporary transaction posted.",
    )
    assert second_result == transaction_services.TransactionPostResult(
        False,
        "Transaction is already posted.",
    )
    assert get_transaction_by_id(1).posting_status == "posted"
    assert get_total_centavos("expense") == 12345
    assert get_current_balance_centavos() == -12345


def test_failed_database_post_leaves_status_and_totals_unchanged():
    seed_temporary_expense(12345)

    with transaction_repository.connect_database() as connection:
        connection.execute(
            """
            CREATE TRIGGER prevent_temporary_post
            BEFORE UPDATE OF posting_status ON transactions
            WHEN OLD.posting_status = 'temporary'
              AND NEW.posting_status = 'posted'
            BEGIN
                SELECT RAISE(ABORT, 'posting unavailable');
            END
            """
        )
        connection.commit()

    result = transaction_services.post_transaction_by_id(1)

    assert result == transaction_services.TransactionPostResult(
        False,
        "Temporary transaction could not be posted.",
    )
    assert get_transaction_by_id(1).posting_status == "temporary"
    assert get_total_centavos("expense") == 0
    assert get_current_balance_centavos() == 0


def test_delete_temporary_transaction_returns_status_preserving_record(
    monkeypatch,
):
    transaction = make_transaction()
    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        Mock(return_value=transaction),
    )
    monkeypatch.setattr(
        transaction_services,
        "delete_transaction",
        Mock(return_value=True),
    )

    result = transaction_services.delete_transaction_by_id(17)

    assert result == transaction_services.TransactionDeleteResult(
        True,
        "Temporary transaction deleted.",
        transaction,
    )
    assert result.deleted_transaction.posting_status == "temporary"


@pytest.mark.parametrize(
    "repository_value",
    [False, sqlite3.OperationalError("database unavailable")],
)
def test_delete_temporary_transaction_handles_repository_failure(
    monkeypatch,
    repository_value,
):
    if isinstance(repository_value, Exception):
        delete_transaction = Mock(side_effect=repository_value)
    else:
        delete_transaction = Mock(return_value=repository_value)
    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        Mock(return_value=make_transaction()),
    )
    monkeypatch.setattr(
        transaction_services,
        "delete_transaction",
        delete_transaction,
    )

    result = transaction_services.delete_transaction_by_id(17)

    assert result == transaction_services.TransactionDeleteResult(
        False,
        "Temporary transaction could not be deleted.",
    )


def test_delete_transaction_handles_lookup_failure(monkeypatch):
    delete_transaction = Mock()
    monkeypatch.setattr(
        transaction_services,
        "get_transaction_by_id",
        Mock(side_effect=sqlite3.OperationalError),
    )
    monkeypatch.setattr(
        transaction_services,
        "delete_transaction",
        delete_transaction,
    )

    result = transaction_services.delete_transaction_by_id(17)

    assert result == transaction_services.TransactionDeleteResult(
        False,
        "Transaction could not be deleted.",
    )
    delete_transaction.assert_not_called()


@pytest.mark.parametrize(
    ("repository_value", "success", "message"),
    [
        (True, True, "Temporary transaction restored."),
        (False, False, "Temporary transaction could not be restored."),
        (
            sqlite3.OperationalError("database unavailable"),
            False,
            "Temporary transaction could not be restored.",
        ),
    ],
)
def test_restore_temporary_transaction_returns_stable_result(
    monkeypatch,
    repository_value,
    success,
    message,
):
    if isinstance(repository_value, Exception):
        restore_transaction = Mock(side_effect=repository_value)
    else:
        restore_transaction = Mock(return_value=repository_value)
    monkeypatch.setattr(
        transaction_services,
        "restore_transaction",
        restore_transaction,
    )

    result = transaction_services.restore_deleted_transaction(
        make_transaction()
    )

    assert result == transaction_services.TransactionRestoreResult(
        success,
        message,
    )


def test_delete_and_restore_keep_temporary_transaction_non_posting():
    seed_temporary_expense(12345)

    delete_result = transaction_services.delete_transaction_by_id(1)
    assert delete_result.success is True
    assert delete_result.message == "Temporary transaction deleted."
    assert get_transaction_by_id(1) is None
    assert get_total_centavos("expense") == 0
    assert get_current_balance_centavos() == 0

    restore_result = transaction_services.restore_deleted_transaction(
        delete_result.deleted_transaction
    )

    assert restore_result == transaction_services.TransactionRestoreResult(
        True,
        "Temporary transaction restored.",
    )
    assert get_transaction_by_id(1).posting_status == "temporary"
    assert get_total_centavos("expense") == 0
    assert get_current_balance_centavos() == 0
