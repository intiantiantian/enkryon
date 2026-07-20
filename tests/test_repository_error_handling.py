from contextlib import contextmanager
import sqlite3

import pytest

from database import account_repository
from database import category_group_repository
from database import category_repository
from database import settings_repository
from database import transaction_repository


@contextmanager
def failing_managed_connection():
    raise sqlite3.OperationalError("database unavailable")
    yield


@pytest.mark.parametrize(
    ("repository", "operation", "expected_result"),
    [
        (
            account_repository,
            lambda: account_repository.insert_account("Cash"),
            False,
        ),
        (
            account_repository,
            lambda: account_repository.delete_account(1),
            (False, "error"),
        ),
        (
            category_group_repository,
            lambda: category_group_repository.insert_category_group(
                "Food",
                "expense",
            ),
            (False, "error"),
        ),
        (
            category_repository,
            lambda: category_repository.insert_category(1, "Dining"),
            (False, "error"),
        ),
        (
            transaction_repository,
            lambda: transaction_repository.insert_transaction(
                account_id=1,
                amount_centavos=12345,
                category_id=1,
                date_time="2026-07-20 12:00:00",
                notes="Lunch",
            ),
            False,
        ),
        (
            settings_repository,
            settings_repository.clear_database,
            False,
        ),
    ],
)
def test_repository_mutations_return_failure_on_database_error(
    monkeypatch,
    repository,
    operation,
    expected_result,
):
    monkeypatch.setattr(
        repository,
        "managed_connection",
        failing_managed_connection,
    )

    assert operation() == expected_result
