from contextlib import contextmanager
from datetime import datetime, timedelta

from database import connection as database_connection
from database import transaction_repository


HISTORY_SIZE = 10_000
RESULT_LIMIT = 25


def seed_large_transaction_history(connection):
    connection.execute(
        "INSERT INTO accounts (name) VALUES ('Cash'), ('Savings')"
    )
    connection.execute(
        """
        INSERT INTO category_groups (name, transaction_type)
        VALUES ('Salary', 'income'), ('Food', 'expense')
        """
    )
    connection.execute(
        """
        INSERT INTO categories (group_id, name)
        VALUES (1, 'Paycheck'), (2, 'Lunch')
        """
    )

    starting_datetime = datetime(2026, 1, 1)
    transactions = [
        (
            1 if transaction_id % 2 else 2,
            transaction_id * 100,
            2 if transaction_id % 3 == 0 else 1,
            (
                starting_datetime
                + timedelta(minutes=transaction_id)
            ).strftime("%Y-%m-%d %H:%M:%S"),
            f"Transaction {transaction_id}",
        )
        for transaction_id in range(1, HISTORY_SIZE + 1)
    ]
    connection.executemany(
        """
        INSERT INTO transactions (
            account_id,
            amount_centavos,
            category_id,
            date_time,
            notes
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        transactions,
    )
    connection.commit()
    connection.execute("ANALYZE")


@contextmanager
def keep_connection_open(connection):
    yield connection


def run_indexed_query(connection, **filters):
    traced_statements = []
    connection.set_trace_callback(traced_statements.append)

    try:
        transactions = transaction_repository.get_transactions(
            limit=RESULT_LIMIT,
            **filters,
        )
    finally:
        connection.set_trace_callback(None)

    select_statement = next(
        statement
        for statement in traced_statements
        if statement.lstrip().startswith(
            "SELECT transactions.id"
        )
    )
    query_plan = [
        row[3]
        for row in connection.execute(
            f"EXPLAIN QUERY PLAN {select_statement}"
        ).fetchall()
    ]
    return transactions, query_plan


def transaction_ids(transactions):
    return [
        transaction.transaction_id
        for transaction in transactions
    ]


def test_large_history_queries_use_transaction_indexes(
    monkeypatch,
):
    connection = database_connection.connect_database()

    try:
        seed_large_transaction_history(connection)
        monkeypatch.setattr(
            transaction_repository,
            "managed_connection",
            lambda: keep_connection_open(connection),
        )

        recent_transactions, recent_plan = run_indexed_query(
            connection
        )
        account_transactions, account_plan = run_indexed_query(
            connection,
            account_id=2,
        )
        category_transactions, category_plan = run_indexed_query(
            connection,
            category_id=2,
        )
    finally:
        connection.close()

    assert transaction_ids(recent_transactions) == list(
        range(10_000, 9_975, -1)
    )
    assert transaction_ids(account_transactions) == list(
        range(10_000, 9_950, -2)
    )
    assert transaction_ids(category_transactions) == list(
        range(9_999, 9_924, -3)
    )
    assert any(
        "transactions_history_order_index" in step
        for step in recent_plan
    )
    assert any(
        "transactions_account_history_index" in step
        for step in account_plan
    )
    assert any(
        "transactions_category_history_index" in step
        for step in category_plan
    )
