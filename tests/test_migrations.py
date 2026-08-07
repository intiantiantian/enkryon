from pathlib import Path
import shutil
import sqlite3

import pytest

from database import migrations


LEGACY_V0_3_0_DATABASE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "enkryon_v0_3_0.db"
)


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


def create_centavo_transaction_database(amount="12.34"):
    connection = create_legacy_transaction_database(amount)

    connection.execute("BEGIN")
    migrations.migrate_transactions_to_centavos(connection)
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


def test_upgrades_v0_3_0_database_file_without_data_loss(
    tmp_path,
    monkeypatch,
):
    upgraded_database = tmp_path / "upgraded_v0_3_0.db"
    shutil.copyfile(
        LEGACY_V0_3_0_DATABASE,
        upgraded_database,
    )

    def connect_upgraded_database():
        connection = sqlite3.connect(upgraded_database)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    monkeypatch.setattr(
        migrations,
        "connect_database",
        connect_upgraded_database,
    )

    migrations.run_migrations()
    migrations.run_migrations()

    connection = connect_upgraded_database()

    try:
        migration_rows = connection.execute(
            """
            SELECT version, name
            FROM schema_migrations
            ORDER BY version
            """
        ).fetchall()

        transaction_columns = {
            row[1]: row[2]
            for row in connection.execute(
                "PRAGMA table_info(transactions)"
            ).fetchall()
        }

        record_counts = {
            table_name: connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]
            for table_name in (
                "accounts",
                "category_groups",
                "categories",
                "transactions",
                "account_transfers",
            )
        }

        transactions = connection.execute(
            """
            SELECT
                id,
                account_id,
                amount_centavos,
                category_id,
                date_time,
                notes,
                posting_status
            FROM transactions
            ORDER BY id
            """
        ).fetchall()

        totals = dict(
            connection.execute(
                """
                SELECT
                    category_groups.transaction_type,
                    SUM(transactions.amount_centavos)
                FROM transactions
                INNER JOIN categories
                    ON transactions.category_id =
                       categories.category_id
                INNER JOIN category_groups
                    ON categories.group_id =
                       category_groups.group_id
                GROUP BY category_groups.transaction_type
                """
            ).fetchall()
        )

        foreign_key_violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()
    finally:
        connection.close()

    assert migration_rows == [
        (1, "initial_schema"),
        (2, "transactions_amount_centavos"),
        (3, "validation_constraints"),
        (4, "transaction_history_indexes"),
        (5, "account_transfers"),
        (6, "transaction_posting_status"),
        (7, "account_transfer_kinds"),
        (8, "pass_through_movements"),
        (9, "pass_through_balance_neutrality"),
    ]
    assert "amount" not in transaction_columns
    assert transaction_columns["amount_centavos"] == "INTEGER"
    assert transaction_columns["posting_status"] == "TEXT"
    assert record_counts == {
        "accounts": 2,
        "category_groups": 2,
        "categories": 2,
        "transactions": 3,
        "account_transfers": 0,
    }
    assert transactions == [
        (
            7,
            1,
            123456,
            1,
            "2026-06-01 08:00:00",
            "June salary",
            "posted",
        ),
        (
            11,
            1,
            1,
            2,
            "2026-06-02 12:30:00",
            "Centavo boundary",
            "posted",
        ),
        (
            15,
            2,
            1020,
            2,
            "2026-06-03 09:15:00",
            None,
            "posted",
        ),
    ]
    assert totals == {
        "income": 123456,
        "expense": 1021,
    }
    assert totals["income"] - totals["expense"] == 122435
    assert foreign_key_violations == []


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
        (3, "validation_constraints"),
        (4, "transaction_history_indexes"),
        (5, "account_transfers"),
        (6, "transaction_posting_status"),
        (7, "account_transfer_kinds"),
        (8, "pass_through_movements"),
        (9, "pass_through_balance_neutrality"),
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
        + ((10, "failing_migration", failing_migration),),
    )

    with pytest.raises(RuntimeError, match="migration failed"):
        migrations.run_migrations()

    connection = migrations.connect_database()

    try:
        migration_record = connection.execute(
            '''
            SELECT version
            FROM schema_migrations
            WHERE version = 10
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


def test_adds_transaction_posting_status_with_safe_default():
    connection = create_centavo_transaction_database()

    try:
        connection.execute("BEGIN")
        migrations.add_transaction_constraints(connection)
        migrations.add_transaction_posting_status(connection)
        connection.commit()

        columns = {
            row[1]: row
            for row in connection.execute(
                "PRAGMA table_info(transactions)"
            ).fetchall()
        }
        stored_status = connection.execute(
            "SELECT posting_status FROM transactions WHERE id = 7"
        ).fetchone()[0]

        connection.execute(
            """
            INSERT INTO transactions (
                account_id,
                amount_centavos,
                category_id,
                date_time
            )
            VALUES (1, 500, 1, '2026-07-16 09:00:00')
            """
        )
        default_status = connection.execute(
            "SELECT posting_status FROM transactions WHERE id = 8"
        ).fetchone()[0]
        status_index_columns = [
            (row[2], row[3])
            for row in connection.execute(
                "PRAGMA index_xinfo("
                "'transactions_posting_status_history_index'"
                ")"
            ).fetchall()
            if row[5]
        ]

        connection.execute(
            "UPDATE transactions SET posting_status = 'temporary' "
            "WHERE id = 8"
        )

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "UPDATE transactions SET posting_status = 'invalid' "
                "WHERE id = 8"
            )
    finally:
        connection.close()

    assert columns["posting_status"][2] == "TEXT"
    assert columns["posting_status"][3] == 1
    assert columns["posting_status"][4] == "'posted'"
    assert stored_status == "posted"
    assert default_status == "posted"
    assert status_index_columns == [
        ("posting_status", 0),
        ("date_time", 1),
        ("id", 1),
    ]


def test_adds_transaction_history_indexes():
    connection = create_centavo_transaction_database()

    try:
        migrations.add_transaction_history_indexes(connection)
        connection.commit()

        index_columns = {
            index_name: [
                (row[2], row[3])
                for row in connection.execute(
                    f"PRAGMA index_xinfo('{index_name}')"
                ).fetchall()
                if row[5]
            ]
            for index_name in (
                "transactions_history_order_index",
                "transactions_account_history_index",
                "transactions_category_history_index",
            )
        }
    finally:
        connection.close()

    assert index_columns == {
        "transactions_history_order_index": [
            ("date_time", 1),
            ("id", 1),
        ],
        "transactions_account_history_index": [
            ("account_id", 0),
            ("date_time", 1),
            ("id", 1),
        ],
        "transactions_category_history_index": [
            ("category_id", 0),
            ("date_time", 1),
            ("id", 1),
        ],
    }


def test_adds_account_transfer_table_constraints_and_indexes():
    connection = create_centavo_transaction_database()

    try:
        connection.execute(
            "INSERT INTO accounts (name) VALUES ('Savings')"
        )
        migrations.create_account_transfers_table(connection)
        migrations.create_account_transfers_table(connection)
        connection.commit()

        columns = {
            row[1]: row[2]
            for row in connection.execute(
                "PRAGMA table_info(account_transfers)"
            ).fetchall()
        }
        foreign_keys = {
            (row[3], row[2])
            for row in connection.execute(
                "PRAGMA foreign_key_list(account_transfers)"
            ).fetchall()
        }
        index_columns = {
            index_name: [
                (row[2], row[3])
                for row in connection.execute(
                    f"PRAGMA index_xinfo('{index_name}')"
                ).fetchall()
                if row[5]
            ]
            for index_name in (
                "account_transfers_history_order_index",
                "account_transfers_source_history_index",
                "account_transfers_destination_history_index",
            )
        }

        connection.execute(
            '''
            INSERT INTO account_transfers (
                source_account_id,
                destination_account_id,
                amount_centavos,
                date_time,
                notes
            )
            VALUES (
                1,
                2,
                10025,
                '2026-08-04 14:30:00',
                'Valid transfer'
            )
            '''
        )
        connection.commit()

        invalid_inserts = (
            '''
            INSERT INTO account_transfers (
                source_account_id,
                destination_account_id,
                amount_centavos,
                date_time
            )
            VALUES (1, 1, 100, '2026-08-04 14:30:00')
            ''',
            '''
            INSERT INTO account_transfers (
                source_account_id,
                destination_account_id,
                amount_centavos,
                date_time
            )
            VALUES (1, 2, 0, '2026-08-04 14:30:00')
            ''',
            '''
            INSERT INTO account_transfers (
                source_account_id,
                destination_account_id,
                amount_centavos,
                date_time
            )
            VALUES (1, 2, 12.5, '2026-08-04 14:30:00')
            ''',
            '''
            INSERT INTO account_transfers (
                source_account_id,
                destination_account_id,
                amount_centavos,
                date_time
            )
            VALUES (1, 2, 100, '2026-08-04')
            ''',
            '''
            INSERT INTO account_transfers (
                source_account_id,
                destination_account_id,
                amount_centavos,
                date_time
            )
            VALUES (999, 2, 100, '2026-08-04 14:30:00')
            ''',
        )

        for statement in invalid_inserts:
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(statement)
            connection.rollback()

        stored_transfer = connection.execute(
            '''
            SELECT
                source_account_id,
                destination_account_id,
                amount_centavos,
                date_time,
                notes
            FROM account_transfers
            '''
        ).fetchone()
    finally:
        connection.close()

    assert columns == {
        "id": "INTEGER",
        "source_account_id": "INTEGER",
        "destination_account_id": "INTEGER",
        "amount_centavos": "INTEGER",
        "date_time": "TEXT",
        "notes": "TEXT",
    }
    assert foreign_keys == {
        ("source_account_id", "accounts"),
        ("destination_account_id", "accounts"),
    }
    assert index_columns == {
        "account_transfers_history_order_index": [
            ("date_time", 1),
            ("id", 1),
        ],
        "account_transfers_source_history_index": [
            ("source_account_id", 0),
            ("date_time", 1),
            ("id", 1),
        ],
        "account_transfers_destination_history_index": [
            ("destination_account_id", 0),
            ("date_time", 1),
            ("id", 1),
        ],
    }
    assert stored_transfer == (
        1,
        2,
        10025,
        "2026-08-04 14:30:00",
        "Valid transfer",
    )


def test_adds_transaction_amount_and_datetime_constraints():
    connection = create_centavo_transaction_database()

    try:
        connection.execute("BEGIN")
        migrations.add_transaction_constraints(connection)
        connection.commit()

        stored_transaction = connection.execute(
            '''
            SELECT id, amount_centavos, date_time
            FROM transactions
            '''
        ).fetchone()

        assert stored_transaction == (
            7,
            1234,
            "2026-07-16 08:00:00",
        )

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                '''
                INSERT INTO transactions (
                    account_id,
                    amount_centavos,
                    category_id,
                    date_time
                )
                VALUES (1, 0, 1, '2026-07-16 09:00:00')
                '''
            )
        connection.rollback()

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                '''
                INSERT INTO transactions (
                    account_id,
                    amount_centavos,
                    category_id,
                    date_time
                )
                VALUES (1, 12.5, 1, '2026-07-16 09:00:00')
                '''
            )
        connection.rollback()

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                '''
                INSERT INTO transactions (
                    account_id,
                    amount_centavos,
                    category_id,
                    date_time
                )
                VALUES (1, 500, 1, '2026-02-30 09:00:00')
                '''
            )
        connection.rollback()
    finally:
        connection.close()


def test_rejects_existing_transaction_constraint_violation():
    connection = create_centavo_transaction_database("0")

    try:
        with pytest.raises(
            migrations.MigrationError,
            match=r"\[7\]",
        ):
            migrations.add_transaction_constraints(connection)
    finally:
        connection.close()


def test_adds_normalized_name_and_type_constraints():
    connection = create_centavo_transaction_database()

    try:
        migrations.add_entity_constraints(connection)
        connection.commit()

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO accounts (name) VALUES (' cash ')"
            )
        connection.rollback()

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO accounts (name) VALUES ('cash')"
            )
        connection.rollback()

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                '''
                INSERT INTO category_groups (
                    name,
                    transaction_type
                )
                VALUES ('Invalid', 'transfer')
                '''
            )
        connection.rollback()

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                '''
                UPDATE category_groups
                SET transaction_type = 'expense'
                WHERE group_id = 1
                '''
            )
        connection.rollback()

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                '''
                INSERT INTO categories (group_id, name)
                VALUES (1, ' ')
                '''
            )
        connection.rollback()
    finally:
        connection.close()


def test_category_name_is_unique_within_transaction_type():
    connection = create_centavo_transaction_database()

    try:
        migrations.add_entity_constraints(connection)
        connection.commit()

        cursor = connection.execute(
            '''
            INSERT INTO category_groups (name, transaction_type)
            VALUES ('Other Income', 'income')
            '''
        )
        income_group_id = cursor.lastrowid
        connection.commit()

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                '''
                INSERT INTO categories (group_id, name)
                VALUES (?, 'paycheck')
                ''',
                (income_group_id,),
            )
        connection.rollback()

        cursor = connection.execute(
            '''
            INSERT INTO category_groups (name, transaction_type)
            VALUES ('Food', 'expense')
            '''
        )
        expense_group_id = cursor.lastrowid
        connection.commit()

        connection.execute(
            '''
            INSERT INTO categories (group_id, name)
            VALUES (?, 'Paycheck')
            ''',
            (expense_group_id,),
        )
        connection.commit()

        expense_category = connection.execute(
            '''
            SELECT categories.name
            FROM categories
            INNER JOIN category_groups
                ON categories.group_id =
                   category_groups.group_id
            WHERE category_groups.transaction_type = 'expense'
            '''
        ).fetchone()

        assert expense_category == ("Paycheck",)
    finally:
        connection.close()


def test_rejects_existing_entity_constraint_violation():
    connection = create_centavo_transaction_database()

    try:
        connection.execute(
            "UPDATE accounts SET name = ' Cash ' WHERE id = 1"
        )
        connection.commit()

        with pytest.raises(
            migrations.MigrationError,
            match="accounts",
        ):
            migrations.add_entity_constraints(connection)
    finally:
        connection.close()
