import sqlite3

from database.account_repository import insert_account
from database.category_group_repository import insert_category_group
from database.category_repository import insert_category
from database.interest_repository import (
    get_interest_accruals,
    insert_interest_profile,
)
from database.transaction_repository import (
    get_current_balance_centavos,
    get_transaction_by_id,
    insert_transaction,
)
from services.interest_services import (
    generate_missing_interest_accruals,
    get_interest_estimate_summary,
    get_interest_reconciliation_preview,
    reconcile_interest_credit,
)


def seed_interest_reconciliation():
    assert insert_account("Savings") is True
    assert insert_category_group("Income", "income") == (True, None)
    assert insert_category_group("Expense", "expense") == (True, None)
    assert insert_category(1, "Salary") == (True, None)
    assert insert_category(1, "Bank Interest") == (True, None)
    assert insert_category(2, "Food") == (True, None)
    assert insert_transaction(
        1,
        1_000_000,
        1,
        "2026-08-01 09:00:00",
        None,
    ) is True
    profile_id = insert_interest_profile(
        1,
        3_650_000,
        "2026-08-02",
        enabled=True,
    )
    assert profile_id is not False
    generate_missing_interest_accruals(1, "2026-08-03")


def test_preview_sums_only_estimated_days_through_credit_date():
    seed_interest_reconciliation()

    preview = get_interest_reconciliation_preview(1, "2026-08-02")

    assert preview.accrual_count == 1
    assert preview.estimated_centavos == 100


def test_reconciliation_posts_actual_income_and_links_estimate_period():
    seed_interest_reconciliation()

    result = reconcile_interest_credit(
        account_id=1,
        actual_amount_centavos=250,
        credit_date="2026-08-03",
        category_id=2,
    )

    assert result.success is True
    assert result.accrual_count == 2
    assert result.estimated_centavos == 200
    assert result.actual_centavos == 250
    assert result.variance_centavos == 50

    transaction = get_transaction_by_id(result.posted_transaction_id)
    assert transaction.account_id == 1
    assert transaction.amount_centavos == 250
    assert transaction.category_id == 2
    assert transaction.transaction_type == "income"
    assert transaction.posting_status == "posted"
    assert transaction.date_time == "2026-08-03 12:00:00"
    assert transaction.notes == "Bank interest credit"

    accruals = get_interest_accruals(1)
    assert [item.status for item in accruals] == [
        "reconciled",
        "reconciled",
    ]
    assert {
        item.posted_transaction_id for item in accruals
    } == {result.posted_transaction_id}
    assert get_interest_estimate_summary(1).rounded_centavos == 0
    assert get_current_balance_centavos(1) == 1_000_250


def test_actual_credit_may_differ_below_estimate_without_rewriting_estimates():
    seed_interest_reconciliation()

    result = reconcile_interest_credit(
        account_id=1,
        actual_amount_centavos=175,
        credit_date="2026-08-03",
        category_id=2,
    )

    assert result.success is True
    assert result.estimated_centavos == 200
    assert result.variance_centavos == -25
    accruals = get_interest_accruals(1)
    assert [item.accrued_whole_centavos for item in accruals] == [100, 100]


def test_repeated_reconciliation_cannot_post_same_estimate_period_twice():
    seed_interest_reconciliation()
    first = reconcile_interest_credit(
        account_id=1,
        actual_amount_centavos=200,
        credit_date="2026-08-03",
        category_id=2,
    )

    second = reconcile_interest_credit(
        account_id=1,
        actual_amount_centavos=200,
        credit_date="2026-08-03",
        category_id=2,
    )

    assert first.success is True
    assert second.success is False
    assert "no estimated interest days" in second.message.lower()
    assert get_current_balance_centavos(1) == 1_000_200


def test_reconciliation_rejects_expense_or_missing_category_without_changes():
    seed_interest_reconciliation()

    expense = reconcile_interest_credit(
        account_id=1,
        actual_amount_centavos=200,
        credit_date="2026-08-03",
        category_id=3,
    )
    missing = reconcile_interest_credit(
        account_id=1,
        actual_amount_centavos=200,
        credit_date="2026-08-03",
        category_id=999,
    )

    assert expense.success is False
    assert missing.success is False
    assert get_current_balance_centavos(1) == 1_000_000
    assert [item.status for item in get_interest_accruals(1)] == [
        "estimated",
        "estimated",
    ]


def test_invalid_actual_amount_and_date_do_not_post():
    seed_interest_reconciliation()

    zero = reconcile_interest_credit(
        account_id=1,
        actual_amount_centavos=0,
        credit_date="2026-08-03",
        category_id=2,
    )
    bad_date = reconcile_interest_credit(
        account_id=1,
        actual_amount_centavos=200,
        credit_date="not-a-date",
        category_id=2,
    )

    assert zero.success is False
    assert bad_date.success is False
    assert get_current_balance_centavos(1) == 1_000_000


def test_atomic_repository_failure_rolls_back_inserted_income(monkeypatch):
    seed_interest_reconciliation()
    from database import connection as database_connection

    real_connect = database_connection.connect_database

    def connect_with_abort_trigger():
        connection = real_connect()
        connection.execute(
            '''
            CREATE TRIGGER IF NOT EXISTS reject_reconciliation
            BEFORE UPDATE OF status ON account_interest_accruals
            WHEN NEW.status = 'reconciled'
            BEGIN
                SELECT RAISE(ABORT, 'test rollback');
            END
            '''
        )
        return connection

    monkeypatch.setattr(
        database_connection,
        "connect_database",
        connect_with_abort_trigger,
    )

    result = reconcile_interest_credit(
        account_id=1,
        actual_amount_centavos=200,
        credit_date="2026-08-03",
        category_id=2,
    )

    assert result.success is False
    assert "no financial changes" in result.message.lower()
    assert get_current_balance_centavos(1) == 1_000_000
    assert [item.status for item in get_interest_accruals(1)] == [
        "estimated",
        "estimated",
    ]


def test_future_credit_date_is_rejected_without_generating_future_accruals():
    from datetime import date, timedelta

    seed_interest_reconciliation()
    future_date = (date.today() + timedelta(days=1)).isoformat()

    result = reconcile_interest_credit(
        account_id=1,
        actual_amount_centavos=200,
        credit_date=future_date,
        category_id=2,
    )

    assert result.success is False
    assert "future" in result.message.lower()
    assert get_current_balance_centavos(1) == 1_000_000
