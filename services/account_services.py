import sqlite3
from typing import NamedTuple

from database.account_repository import (
    delete_account,
    get_all_accounts,
    insert_account,
    update_account,
)


class AccountActionResult(NamedTuple):
    success: bool
    message: str


def get_accounts_for_view():
    return get_all_accounts()


def create_account(account_name):
    account_name = (account_name or "").strip()

    if not account_name:
        return AccountActionResult(
            False,
            "Account name cannot be empty.",
        )

    try:
        accounts = get_accounts_for_view()
    except sqlite3.Error:
        return AccountActionResult(
            False,
            "Account could not be added.",
        )

    if _account_name_exists(accounts, account_name):
        return AccountActionResult(
            False,
            f"Account '{account_name}' already exists.",
        )

    if not insert_account(account_name):
        return AccountActionResult(
            False,
            "Account could not be added.",
        )

    return AccountActionResult(
        True,
        f"Account '{account_name}' added successfully.",
    )


def rename_account(account_id, new_name):
    new_name = (new_name or "").strip()

    if not new_name:
        return AccountActionResult(
            False,
            "New account name cannot be empty.",
        )

    try:
        accounts = get_accounts_for_view()
    except sqlite3.Error:
        return AccountActionResult(
            False,
            "Account could not be renamed.",
        )

    if not any(account.account_id == account_id for account in accounts):
        return AccountActionResult(
            False,
            "Account no longer exists.",
        )

    if _account_name_exists(
        accounts,
        new_name,
        exclude_account_id=account_id,
    ):
        return AccountActionResult(
            False,
            f"Account name '{new_name}' already exists.",
        )

    if not update_account(account_id, new_name):
        return AccountActionResult(
            False,
            "Account could not be renamed.",
        )

    return AccountActionResult(
        True,
        f"Account renamed to '{new_name}' successfully.",
    )


def remove_account(account_id):
    success, reason = delete_account(account_id)

    if success:
        return AccountActionResult(
            True,
            "Account deleted successfully.",
        )

    if reason == "referenced":
        return AccountActionResult(
            False,
            "Cannot delete account because it has existing "
            "transactions or transfers.",
        )

    return AccountActionResult(
        False,
        "Account could not be deleted.",
    )


def _account_name_exists(
    accounts,
    account_name,
    exclude_account_id=None,
):
    normalized_name = account_name.casefold()

    return any(
        account.account_id != exclude_account_id
        and account.name.strip().casefold() == normalized_name
        for account in accounts
    )
