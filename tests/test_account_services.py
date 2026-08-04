import sqlite3
from unittest.mock import Mock

import pytest

from database.records import AccountRecord
from services import account_services


def patch_dependency(
    monkeypatch,
    name,
    *,
    return_value=None,
    side_effect=None,
):
    dependency = Mock(
        return_value=return_value,
        side_effect=side_effect,
    )
    monkeypatch.setattr(account_services, name, dependency)
    return dependency


def test_get_accounts_for_view_forwards_repository_records(monkeypatch):
    accounts = [AccountRecord(account_id=1, name="Cash")]
    get_all_accounts = patch_dependency(
        monkeypatch,
        "get_all_accounts",
        return_value=accounts,
    )

    result = account_services.get_accounts_for_view()

    assert result is accounts
    get_all_accounts.assert_called_once_with()


@pytest.mark.parametrize(
    ("account_name", "accounts", "reads_accounts", "message"),
    [
        ("   ", [], False, "Account name cannot be empty."),
        (
            " cash ",
            [AccountRecord(account_id=1, name="Cash")],
            True,
            "Account 'cash' already exists.",
        ),
    ],
)
def test_create_account_rejects_invalid_name(
    monkeypatch,
    account_name,
    accounts,
    reads_accounts,
    message,
):
    get_accounts_for_view = patch_dependency(
        monkeypatch,
        "get_accounts_for_view",
        return_value=accounts,
    )
    insert_account = patch_dependency(monkeypatch, "insert_account")

    result = account_services.create_account(account_name)

    assert result == account_services.AccountActionResult(False, message)
    assert get_accounts_for_view.called is reads_accounts
    insert_account.assert_not_called()


@pytest.mark.parametrize(
    ("repository_result", "success", "message"),
    [
        (True, True, "Account 'Cash' added successfully."),
        (False, False, "Account could not be added."),
    ],
)
def test_create_account_returns_repository_outcome(
    monkeypatch,
    repository_result,
    success,
    message,
):
    patch_dependency(
        monkeypatch,
        "get_accounts_for_view",
        return_value=[],
    )
    insert_account = patch_dependency(
        monkeypatch,
        "insert_account",
        return_value=repository_result,
    )

    result = account_services.create_account(" Cash ")

    assert result == account_services.AccountActionResult(success, message)
    insert_account.assert_called_once_with("Cash")


@pytest.mark.parametrize(
    ("action", "arguments", "message", "write_name"),
    [
        (
            account_services.create_account,
            ("Cash",),
            "Account could not be added.",
            "insert_account",
        ),
        (
            account_services.rename_account,
            (1, "Wallet"),
            "Account could not be renamed.",
            "update_account",
        ),
    ],
)
def test_account_action_returns_failure_when_account_read_fails(
    monkeypatch,
    action,
    arguments,
    message,
    write_name,
):
    patch_dependency(
        monkeypatch,
        "get_accounts_for_view",
        side_effect=sqlite3.OperationalError,
    )
    write = patch_dependency(monkeypatch, write_name)

    result = action(*arguments)

    assert result == account_services.AccountActionResult(False, message)
    write.assert_not_called()


@pytest.mark.parametrize(
    ("new_name", "accounts", "reads_accounts", "message"),
    [
        ("   ", [], False, "New account name cannot be empty."),
        ("Wallet", [], True, "Account no longer exists."),
        (
            " cash ",
            [
                AccountRecord(account_id=1, name="Cash"),
                AccountRecord(account_id=2, name="Savings"),
            ],
            True,
            "Account name 'cash' already exists.",
        ),
    ],
)
def test_rename_account_rejects_invalid_state(
    monkeypatch,
    new_name,
    accounts,
    reads_accounts,
    message,
):
    get_accounts_for_view = patch_dependency(
        monkeypatch,
        "get_accounts_for_view",
        return_value=accounts,
    )
    update_account = patch_dependency(monkeypatch, "update_account")

    result = account_services.rename_account(2, new_name)

    assert result == account_services.AccountActionResult(False, message)
    assert get_accounts_for_view.called is reads_accounts
    update_account.assert_not_called()


@pytest.mark.parametrize(
    ("repository_result", "success", "message"),
    [
        (True, True, "Account renamed to 'Wallet' successfully."),
        (False, False, "Account could not be renamed."),
    ],
)
def test_rename_account_returns_repository_outcome(
    monkeypatch,
    repository_result,
    success,
    message,
):
    patch_dependency(
        monkeypatch,
        "get_accounts_for_view",
        return_value=[AccountRecord(account_id=1, name="Cash")],
    )
    update_account = patch_dependency(
        monkeypatch,
        "update_account",
        return_value=repository_result,
    )

    result = account_services.rename_account(1, " Wallet ")

    assert result == account_services.AccountActionResult(success, message)
    update_account.assert_called_once_with(1, "Wallet")


@pytest.mark.parametrize(
    ("repository_result", "success", "message"),
    [
        ((True, None), True, "Account deleted successfully."),
        (
            (False, "referenced"),
            False,
            "Cannot delete account because it has existing "
            "transactions or transfers.",
        ),
        ((False, "error"), False, "Account could not be deleted."),
    ],
)
def test_remove_account_returns_repository_outcome(
    monkeypatch,
    repository_result,
    success,
    message,
):
    delete_account = patch_dependency(
        monkeypatch,
        "delete_account",
        return_value=repository_result,
    )

    result = account_services.remove_account(1)

    assert result == account_services.AccountActionResult(success, message)
    delete_account.assert_called_once_with(1)
