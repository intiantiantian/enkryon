from datetime import date

from database.account_repository import insert_account
from database.activity_repository import get_activity
from database.category_group_repository import insert_category_group
from database.category_repository import insert_category
from database.transaction_repository import (
    get_current_balance_centavos,
    get_total_centavos,
    insert_transaction,
)
from database.transfer_repository import insert_transfer
from services.transaction_services import post_transaction_by_id


def seed_mixed_pending_activity():
    assert insert_account("Cash") is True
    assert insert_account("Savings") is True
    assert insert_category_group("Salary", "income") == (True, None)
    assert insert_category_group("Food", "expense") == (True, None)
    assert insert_category(1, "Paycheck") == (True, None)
    assert insert_category(2, "Dining") == (True, None)

    assert insert_transaction(
        1,
        100_000,
        1,
        "2026-08-01 09:00:00",
        "Posted salary",
    ) is True
    assert insert_transaction(
        2,
        5_000,
        1,
        "2026-08-02 09:00:00",
        "Pending bonus",
        posting_status="temporary",
    ) is True
    assert insert_transaction(
        2,
        1_250,
        2,
        "2026-08-03 09:00:00",
        "Posted lunch",
    ) is True
    assert insert_transaction(
        1,
        2_000,
        2,
        "2026-08-04 09:00:00",
        "Pending dinner",
        posting_status="temporary",
    ) is True
    assert insert_transfer(
        1,
        2,
        10_000,
        "2026-08-05 09:00:00",
        "Savings transfer",
    ) is True


def test_mixed_activity_filters_keep_posted_and_pending_semantics_separate():
    seed_mixed_pending_activity()

    all_activity = get_activity()
    posted_income = get_activity(activity_type="income")
    posted_expenses = get_activity(activity_type="expense")
    pending = get_activity(posting_status="temporary")

    assert [row.notes for row in all_activity] == [
        "Savings transfer",
        "Pending dinner",
        "Posted lunch",
        "Pending bonus",
        "Posted salary",
    ]
    assert [row.notes for row in posted_income] == ["Posted salary"]
    assert [row.notes for row in posted_expenses] == ["Posted lunch"]
    assert [row.notes for row in pending] == [
        "Pending dinner",
        "Pending bonus",
    ]
    assert all(row.posting_status == "posted" for row in posted_income)
    assert all(row.posting_status == "posted" for row in posted_expenses)
    assert all(row.posting_status == "temporary" for row in pending)


def test_pending_records_never_enter_financial_totals_before_posting():
    seed_mixed_pending_activity()

    assert get_total_centavos("income") == 100_000
    assert get_total_centavos("expense") == 1_250
    assert get_current_balance_centavos() == 98_750
    assert get_current_balance_centavos(1) == 90_000
    assert get_current_balance_centavos(2) == 8_750


def test_posting_moves_record_from_pending_to_posted_expense_once():
    seed_mixed_pending_activity()

    result = post_transaction_by_id(4)

    assert result.success is True
    assert [row.notes for row in get_activity(
        posting_status="temporary"
    )] == ["Pending bonus"]
    assert [row.notes for row in get_activity(
        activity_type="expense"
    )] == ["Pending dinner", "Posted lunch"]
    assert get_total_centavos("expense") == 3_250
    assert get_current_balance_centavos() == 96_750
    assert get_current_balance_centavos(1) == 88_000

    repeated = post_transaction_by_id(4)

    assert repeated.success is False
    assert get_total_centavos("expense") == 3_250
    assert get_current_balance_centavos() == 96_750


def test_pending_filter_combines_with_search_account_category_and_date():
    seed_mixed_pending_activity()

    matches = get_activity(
        activity_type="expense",
        posting_status="temporary",
        account_id=1,
        category_id=2,
        search_text="dinner",
        start_date=date(2026, 8, 4),
        end_date=date(2026, 8, 4),
    )

    assert [row.notes for row in matches] == ["Pending dinner"]
