import pytest
import sqlite3

from database import migrations


def create_legacy_transaction_database(amount):
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    migrations.create_initial_schema(connection)

    connection.execute(
        "INSERT INTO accounts (name) VALUES ('Cash')"
    )
    connection.execute(
        '''
        INSERT INTO category_groups (name, transaction_type)
        VALUES ('Salary', 'income')
        '''
    )
    connection.execute(
        '''
        INSERT INTO categories (group_id, name)
        VALUES (1, 'Paycheck')
        '''
    )
    connection.execute(
        '''
        INSERT INTO transactions (
            id,
            account_id,
            amount,
            category_id,
            date_time,
            notes
        )
        VALUES (7, 1, ?, 1, '2026-07-16 08:00:00', 'Test')
        ''',
        (amount,),
    )
    connection.commit()

    return connection


def test_migrates_legacy_amount_to_integer_centavos():
    connection = create_legacy_transaction_database("12.34")

    try:
        connection.execute("BEGIN")
        migrations.migrate_transactions_to_centavos(connection)
        connection.commit()

        columns = {
            row[1]: row[2]
            for row in connection.execute(
                "PRAGMA table_info(transactions)"
            ).fetchall()
        }
        transaction = connection.execute(
            '''
            SELECT id, amount_centavos, typeof(amount_centavos)
            FROM transactions
            '''
        ).fetchone()

        cursor = connection.execute(
            '''
            INSERT INTO transactions (
                account_id,
                amount_centavos,
                category_id,
                date_time,
                notes
            )
            VALUES (1, 500, 1, '2026-07-16 09:00:00', 'Next')
            '''
        )

        assert "amount" not in columns
        assert columns["amount_centavos"] == "INTEGER"
        assert transaction == (7, 1234, "integer")
        assert cursor.lastrowid == 8
    finally:
        connection.close()


def test_rejects_unsafe_legacy_amount():
    connection = create_legacy_transaction_database("12.345")

    try:
        with pytest.raises(
            migrations.MigrationError,
            match="Transaction 7",
        ):
            migrations.migrate_transactions_to_centavos(connection)

        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(transactions)"
            ).fetchall()
        }

        assert "amount" in columns
        assert "amount_centavos" not in columns
    finally:
        connection.close()


def get_migration_rows():
    connection = migrations.connect_database()

    try:
        return connection.execute(
            '''
            SELECT version, name
            FROM schema_migrations
            ORDER BY version
            '''
        ).fetchall()
    finally:
        connection.close()


def test_initial_schema_uses_dependency_order(monkeypatch):
    calls = []
    connection = object()

    monkeypatch.setattr(
        migrations,
        "create_accounts_table",
        lambda shared_connection: calls.append(
            ("accounts", shared_connection)
        ),
    )
    monkeypatch.setattr(
        migrations,
        "create_category_groups_table",
        lambda shared_connection: calls.append(
            ("category_groups", shared_connection)
        ),
    )
    monkeypatch.setattr(
        migrations,
        "create_categories_table",
        lambda shared_connection: calls.append(
            ("categories", shared_connection)
        ),
    )
    monkeypatch.setattr(
        migrations,
        "create_transactions_table",
        lambda shared_connection: calls.append(
            ("transactions", shared_connection)
        ),
    )

    migrations.create_initial_schema(connection)

    assert calls == [
        ("accounts", connection),
        ("category_groups", connection),
        ("categories", connection),
        ("transactions", connection),
    ]


def test_run_migrations_is_idempotent():
    migrations.run_migrations()
    migrations.run_migrations()

    assert get_migration_rows() == [
        (1, "initial_schema"),
        (2, "transactions_amount_centavos"),
    ]


def test_failed_migration_is_rolled_back(monkeypatch):
    def failing_migration(connection):
        connection.execute(
            "CREATE TABLE rolled_back_table (id INTEGER)"
        )
        raise RuntimeError("migration failed")

    monkeypatch.setattr(
        migrations,
        "MIGRATIONS",
        migrations.MIGRATIONS
        + ((3, "failing_migration", failing_migration),),
    )

    with pytest.raises(RuntimeError, match="migration failed"):
        migrations.run_migrations()

    connection = migrations.connect_database()

    try:
        migration_record = connection.execute(
            '''
            SELECT version
            FROM schema_migrations
            WHERE version = 3
            '''
        ).fetchone()
        rolled_back_table = connection.execute(
            '''
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'rolled_back_table'
            '''
        ).fetchone()
    finally:
        connection.close()

    assert migration_record is None
    assert rolled_back_table is None