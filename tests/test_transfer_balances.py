from database.account_repository import insert_account
from database.category_group_repository import insert_category_group
from database.category_repository import insert_category
from database.transaction_repository import (
    get_current_balance_centavos,
    get_total_centavos,
    insert_transaction,
)
from database.transfer_repository import (
    delete_transfer,
    get_transfer_balance_centavos,
    insert_transfer,
    update_transfer,
)


def seed_balances():
    assert insert_account("Cash") is True
    assert insert_account("Savings") is True
    assert insert_account("Wallet") is True
    assert insert_category_group("Salary", "income") == (True, None)
    assert insert_category_group("Food", "expense") == (True, None)
    assert insert_category(1, "Paycheck") == (True, None)
    assert insert_category(2, "Lunch") == (True, None)
    assert insert_transaction(
        1,
        100_000,
        1,
        "2026-08-01 09:00:00",
        None,
    ) is True
    assert insert_transaction(
        1,
        5_000,
        2,
        "2026-08-01 10:00:00",
        None,
    ) is True


def test_transfer_changes_only_participating_account_balances():
    seed_balances()
    assert insert_transfer(
        1,
        2,
        25_025,
        "2026-08-02 10:00:00",
        None,
    ) is True

    assert get_current_balance_centavos(1) == 69_975
    assert get_current_balance_centavos(2) == 25_025
    assert get_current_balance_centavos(3) == 0
    assert get_transfer_balance_centavos(1) == -25_025
    assert get_transfer_balance_centavos(2) == 25_025


def test_all_account_balance_is_net_zero_for_transfers():
    seed_balances()
    balance_before_transfer = get_current_balance_centavos()
    assert insert_transfer(
        1,
        2,
        25_025,
        "2026-08-02 10:00:00",
        None,
    ) is True

    assert get_transfer_balance_centavos() == 0
    assert get_current_balance_centavos() == balance_before_transfer


def test_transfers_never_change_income_or_expense_totals():
    seed_balances()
    assert insert_transfer(
        1,
        2,
        25_025,
        "2026-08-02 10:00:00",
        None,
    ) is True

    assert get_total_centavos("income") == 100_000
    assert get_total_centavos("expense") == 5_000
    assert get_total_centavos("income", 2) == 0
    assert get_total_centavos("expense", 2) == 0


def test_transfer_edit_recomputes_every_affected_balance():
    seed_balances()
    assert insert_transfer(
        1,
        2,
        25_000,
        "2026-08-02 10:00:00",
        None,
    ) is True

    assert update_transfer(
        2,
        3,
        10_000,
        "2026-08-02 10:00:00",
        None,
        1,
    ) is True

    assert get_current_balance_centavos(1) == 95_000
    assert get_current_balance_centavos(2) == -10_000
    assert get_current_balance_centavos(3) == 10_000
    assert get_current_balance_centavos() == 95_000


def test_transfer_delete_restores_derived_balances():
    seed_balances()
    assert insert_transfer(
        1,
        2,
        25_000,
        "2026-08-02 10:00:00",
        None,
    ) is True
    assert delete_transfer(1) is True

    assert get_current_balance_centavos(1) == 95_000
    assert get_current_balance_centavos(2) == 0
    assert get_current_balance_centavos() == 95_000
