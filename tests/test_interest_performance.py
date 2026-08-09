from time import perf_counter

from database import migrations
from database.interest_repository import get_interest_accruals
from services.interest_services import generate_missing_interest_accruals


def seed_ten_year_interest_account():
    connection = migrations.connect_database()
    try:
        connection.executescript(
            """
            INSERT INTO accounts (id, name)
            VALUES (1, 'Long-term savings');

            INSERT INTO category_groups (group_id, name, transaction_type)
            VALUES (1, 'Salary', 'income');

            INSERT INTO categories (category_id, group_id, name)
            VALUES (1, 1, 'Opening deposit');

            INSERT INTO transactions (
                account_id,
                amount_centavos,
                category_id,
                date_time,
                notes,
                posting_status
            )
            VALUES (
                1,
                1000000,
                1,
                '2016-01-01 12:00:00',
                NULL,
                'posted'
            );

            INSERT INTO account_interest_profiles (
                account_id,
                annual_rate_micros,
                day_count_basis,
                effective_from,
                enabled
            )
            VALUES (1, 5000000, 365, '2016-01-02', 1);
            """
        )
        connection.commit()
    finally:
        connection.close()


def test_ten_year_accrual_generation_is_batched_and_idempotent():
    seed_ten_year_interest_account()

    started = perf_counter()
    first = generate_missing_interest_accruals(1, "2025-12-31")
    first_elapsed = perf_counter() - started

    started = perf_counter()
    second = generate_missing_interest_accruals(1, "2025-12-31")
    repeat_elapsed = perf_counter() - started

    assert len(first) == 3652
    assert len(second) == 3652
    assert first[0].accrual_date == "2016-01-02"
    assert first[-1].accrual_date == "2025-12-31"
    assert first_elapsed < 5.0
    assert repeat_elapsed < 5.0


def test_interest_range_query_uses_existing_history_index(monkeypatch):
    seed_ten_year_interest_account()
    generate_missing_interest_accruals(1, "2025-12-31")

    from database import connection as database_connection
    from database import interest_repository
    from contextlib import contextmanager

    connection = database_connection.connect_database()
    statements = []

    @contextmanager
    def keep_open():
        yield connection

    try:
        monkeypatch.setattr(
            interest_repository,
            "managed_connection",
            keep_open,
        )
        connection.set_trace_callback(statements.append)
        rows = get_interest_accruals(
            1,
            status="estimated",
            start_date="2025-01-01",
            end_date="2025-12-31",
            limit=25,
        )
        connection.set_trace_callback(None)

        statement = next(
            sql for sql in statements
            if sql.lstrip().startswith("SELECT")
            and "FROM account_interest_accruals" in sql
        )
        plan = [
            row[3]
            for row in connection.execute(
                f"EXPLAIN QUERY PLAN {statement}"
            ).fetchall()
        ]
    finally:
        connection.set_trace_callback(None)
        connection.close()

    assert len(rows) == 25
    assert any(
        "SEARCH account_interest_accruals" in step and "USING" in step
        for step in plan
    )
    assert not any("SCAN account_interest_accruals" in step for step in plan)
