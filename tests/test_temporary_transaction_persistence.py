from database.account_repository import delete_account, insert_account
from database.category_group_repository import insert_category_group
from database.category_repository import delete_category, insert_category
from database.transaction_repository import (
    delete_transaction,
    get_current_balance_centavos,
    get_total_centavos,
    get_transaction_by_id,
    get_transactions,
    insert_transaction,
    restore_transaction,
    update_transaction,
    update_transaction_posting_status,
)


def seed_transaction_dependencies():
    assert insert_account("Cash") is True
    assert insert_account("Savings") is True
    assert insert_category_group("Salary", "income") == (True, None)
    assert insert_category_group("Food", "expense") == (True, None)
    assert insert_category(1, "Paycheck") == (True, None)
    assert insert_category(2, "Lunch") == (True, None)


def test_new_transaction_defaults_to_posted_status():
    seed_transaction_dependencies()

    assert insert_transaction(
        1,
        1000,
        1,
        "2026-08-05 08:00:00",
        "Posted income",
    ) is True

    transaction = get_transaction_by_id(1)

    assert transaction.posting_status == "posted"
    assert get_transactions()[0].posting_status == "posted"


def test_temporary_transaction_round_trips_and_filters_by_status():
    seed_transaction_dependencies()
    assert insert_transaction(
        1,
        1000,
        1,
        "2026-08-05 08:00:00",
        "Posted income",
    ) is True
    assert insert_transaction(
        1,
        250,
        2,
        "2026-08-05 09:00:00",
        "Pending lunch",
        posting_status="temporary",
    ) is True

    temporary = get_transaction_by_id(2)
    temporary_rows = get_transactions(posting_status="temporary")
    posted_rows = get_transactions(posting_status="posted")

    assert temporary.posting_status == "temporary"
    assert [row.transaction_id for row in temporary_rows] == [2]
    assert [row.transaction_id for row in posted_rows] == [1]


def test_edit_preserves_temporary_status_unless_explicitly_changed():
    seed_transaction_dependencies()
    assert insert_transaction(
        1,
        250,
        2,
        "2026-08-05 09:00:00",
        "Pending lunch",
        posting_status="temporary",
    ) is True

    assert update_transaction(
        account_id=2,
        amount_centavos=300,
        category_id=2,
        date_time="2026-08-05 10:00:00",
        notes="Updated pending lunch",
        transaction_id=1,
    ) is True

    transaction = get_transaction_by_id(1)

    assert transaction.account_id == 2
    assert transaction.amount_centavos == 300
    assert transaction.posting_status == "temporary"


def test_posting_status_compare_and_set_prevents_double_post():
    seed_transaction_dependencies()
    assert insert_transaction(
        1,
        250,
        2,
        "2026-08-05 09:00:00",
        "Pending lunch",
        posting_status="temporary",
    ) is True

    assert update_transaction_posting_status(
        1,
        "posted",
        expected_posting_status="temporary",
    ) is True
    assert update_transaction_posting_status(
        1,
        "posted",
        expected_posting_status="temporary",
    ) is False
    assert get_transaction_by_id(1).posting_status == "posted"


def test_invalid_posting_status_is_rejected_without_mutation():
    seed_transaction_dependencies()
    assert insert_transaction(
        1,
        250,
        2,
        "2026-08-05 09:00:00",
        "Pending lunch",
        posting_status="temporary",
    ) is True

    assert insert_transaction(
        1,
        500,
        2,
        "2026-08-05 10:00:00",
        "Invalid",
        posting_status="invalid",
    ) is False
    assert update_transaction_posting_status(1, "invalid") is False
    assert get_transaction_by_id(1).posting_status == "temporary"
    assert [row.transaction_id for row in get_transactions()] == [1]


def test_temporary_transactions_never_change_posted_totals_or_balances():
    seed_transaction_dependencies()
    assert insert_transaction(
        1,
        1000,
        1,
        "2026-08-05 08:00:00",
        "Posted income",
    ) is True
    assert insert_transaction(
        1,
        500,
        1,
        "2026-08-05 09:00:00",
        "Temporary income",
        posting_status="temporary",
    ) is True
    assert insert_transaction(
        1,
        200,
        2,
        "2026-08-05 10:00:00",
        "Temporary expense",
        posting_status="temporary",
    ) is True

    assert get_total_centavos("income") == 1000
    assert get_total_centavos("expense") == 0
    assert get_current_balance_centavos() == 1000
    assert get_current_balance_centavos(account_id=1) == 1000


def test_posting_temporary_transaction_updates_derived_totals_once():
    seed_transaction_dependencies()
    assert insert_transaction(
        1,
        250,
        2,
        "2026-08-05 09:00:00",
        "Pending lunch",
        posting_status="temporary",
    ) is True

    assert get_total_centavos("expense") == 0
    assert update_transaction_posting_status(
        1,
        "posted",
        expected_posting_status="temporary",
    ) is True
    assert get_total_centavos("expense") == 250
    assert get_current_balance_centavos() == -250
    assert update_transaction_posting_status(
        1,
        "posted",
        expected_posting_status="temporary",
    ) is False
    assert get_total_centavos("expense") == 250


def test_restore_preserves_temporary_status():
    seed_transaction_dependencies()
    assert insert_transaction(
        1,
        250,
        2,
        "2026-08-05 09:00:00",
        "Pending lunch",
        posting_status="temporary",
    ) is True
    transaction = get_transaction_by_id(1)

    assert delete_transaction(1) is True
    assert restore_transaction(transaction) is True
    assert get_transaction_by_id(1) == transaction
    assert get_transaction_by_id(1).posting_status == "temporary"


def test_temporary_references_protect_account_and_category_deletion():
    seed_transaction_dependencies()
    assert insert_transaction(
        1,
        250,
        2,
        "2026-08-05 09:00:00",
        "Pending lunch",
        posting_status="temporary",
    ) is True

    assert delete_account(1) == (False, "referenced")
    assert delete_category(2) == (False, "referenced")
