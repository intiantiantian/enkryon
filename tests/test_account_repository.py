from database.account_repository import (
    delete_account,
    get_account_by_id,
    get_all_accounts,
    insert_account,
    update_account,
)


def test_insert_account():
    result = insert_account("Cash")

    assert result is True
    assert get_all_accounts() == [(1, "Cash")]


def test_get_account_by_id():
    insert_account("Cash")

    account = get_account_by_id(1)

    assert account == (1, "Cash")


def test_update_account():
    insert_account("Cash")

    result = update_account(1, "Wallet")

    assert result is True
    assert get_account_by_id(1) == (1, "Wallet")


def test_delete_unused_account():
    insert_account("Cash")

    result, reason = delete_account(1)

    assert result is True
    assert reason is None
    assert get_all_accounts() == []


def test_reject_exact_duplicate_account_name():
    insert_account("Cash")

    result = insert_account("Cash")

    assert result is False
    assert get_all_accounts() == [(1, "Cash")]