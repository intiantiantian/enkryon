from database.account_repository import (
    delete_account,
    get_account_by_id,
    get_all_accounts,
    insert_account,
    update_account,
)
from database.records import AccountRecord
from database.transfer_repository import insert_transfer


def test_insert_account():
    result = insert_account("Cash")
    accounts = get_all_accounts()

    assert result is True
    assert isinstance(accounts[0], AccountRecord)
    assert accounts == [
        AccountRecord(account_id=1, name="Cash")
    ]


def test_get_account_by_id():
    insert_account("Cash")

    account = get_account_by_id(1)

    assert isinstance(account, AccountRecord)
    assert account == AccountRecord(
        account_id=1,
        name="Cash",
    )

def test_update_account():
    insert_account("Cash")

    result = update_account(1, "Wallet")

    assert result is True
    assert get_account_by_id(1) == AccountRecord(
        account_id=1,
        name="Wallet",
    )

def test_delete_unused_account():
    insert_account("Cash")

    result, reason = delete_account(1)

    assert result is True
    assert reason is None
    assert get_all_accounts() == []


def test_delete_account_referenced_by_transfer_is_rejected():
    insert_account("Cash")
    insert_account("Savings")
    assert insert_transfer(
        source_account_id=1,
        destination_account_id=2,
        amount_centavos=10025,
        date_time="2026-08-04 12:30:00",
        notes="Move to savings",
    ) is True

    source_result = delete_account(1)
    destination_result = delete_account(2)

    assert source_result == (False, "referenced")
    assert destination_result == (False, "referenced")


def test_reject_exact_duplicate_account_name():
    insert_account("Cash")

    result = insert_account(" cash ")

    assert result is False
    assert get_all_accounts() == [
        AccountRecord(account_id=1, name="Cash")
    ]

def test_reject_blank_account_name():
    result = insert_account("   ")

    assert result is False
    assert get_all_accounts() == []


def test_reject_duplicate_account_name_when_updating():
    insert_account("Cash")
    insert_account("Savings")

    result = update_account(2, " cash ")

    assert result is False
    assert get_account_by_id(2) == AccountRecord(
        account_id=2,
        name="Savings",
    )
