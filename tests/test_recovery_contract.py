from database import migrations
from database.settings_repository import clear_database


USER_TABLES = {
    "accounts": {
        "columns": ("id", "name"),
        "rows": [
            (3, "Cash / Wallet"),
            (8, "Banco – Savings"),
        ],
    },
    "category_groups": {
        "columns": ("group_id", "name", "transaction_type"),
        "rows": [
            (4, "Food", "expense"),
            (9, "Salary", "income"),
        ],
    },
    "categories": {
        "columns": ("category_id", "group_id", "name"),
        "rows": [
            (6, 4, "Café"),
            (12, 9, "Paycheck"),
        ],
    },
    "transactions": {
        "columns": (
            "id",
            "account_id",
            "amount_centavos",
            "category_id",
            "date_time",
            "notes",
            "posting_status",
        ),
        "rows": [
            (
                15,
                8,
                123456,
                12,
                "2026-07-01 08:30:00",
                "Salary – July",
                "posted",
            ),
            (
                21,
                3,
                1,
                6,
                "2026-07-02 12:00:00",
                None,
                "posted",
            ),
            (
                34,
                3,
                5050,
                6,
                "2026-07-03 19:45:00",
                "",
                "posted",
            ),
        ],
    },
    "account_transfers": {
        "columns": (
            "id",
            "source_account_id",
            "destination_account_id",
            "amount_centavos",
            "date_time",
            "notes",
            "transfer_kind",
            "counterparty",
        ),
        "rows": [
            (
                40,
                8,
                3,
                10025,
                "2026-07-04 09:15:00",
                "Move to wallet",
                "internal",
                None,
            ),
        ],
    },
}

MIGRATION_ROWS = [
    (1, "initial_schema"),
    (2, "transactions_amount_centavos"),
    (3, "validation_constraints"),
    (4, "transaction_history_indexes"),
    (5, "account_transfers"),
    (6, "transaction_posting_status"),
    (7, "account_transfer_kinds"),
    (8, "pass_through_movements"),
]


def read_user_rows(connection):
    user_rows = {}

    for table_name, table_contract in USER_TABLES.items():
        columns = ", ".join(table_contract["columns"])
        primary_key = table_contract["columns"][0]
        user_rows[table_name] = connection.execute(
            f"SELECT {columns} FROM {table_name} "
            f"ORDER BY {primary_key}"
        ).fetchall()

    return user_rows


def read_migration_rows(connection):
    return connection.execute(
        """
        SELECT version, name
        FROM schema_migrations
        ORDER BY version
        """
    ).fetchall()


def seed_recovery_state(connection):
    for table_name, table_contract in USER_TABLES.items():
        columns = ", ".join(table_contract["columns"])
        placeholders = ", ".join(
            "?"
            for _column in table_contract["columns"]
        )
        connection.executemany(
            f"INSERT INTO {table_name} ({columns}) "
            f"VALUES ({placeholders})",
            table_contract["rows"],
        )

    connection.commit()


def test_recovery_contract_matches_current_user_table_columns():
    connection = migrations.connect_database()

    try:
        columns = {
            table_name: tuple(
                row[1]
                for row in connection.execute(
                    f"PRAGMA table_info({table_name})"
                ).fetchall()
            )
            for table_name in USER_TABLES
        }
    finally:
        connection.close()

    assert columns == {
        table_name: table_contract["columns"]
        for table_name, table_contract in USER_TABLES.items()
    }


def test_empty_recovery_state_keeps_schema_history():
    connection = migrations.connect_database()

    try:
        user_rows = read_user_rows(connection)
        migration_rows = read_migration_rows(connection)
        foreign_key_violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()
    finally:
        connection.close()

    assert user_rows == {
        table_name: []
        for table_name in USER_TABLES
    }
    assert migration_rows == MIGRATION_ROWS
    assert foreign_key_violations == []


def test_populated_recovery_state_preserves_exact_values():
    connection = migrations.connect_database()

    try:
        seed_recovery_state(connection)
        user_rows = read_user_rows(connection)
        foreign_key_violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()
    finally:
        connection.close()

    assert user_rows == {
        table_name: table_contract["rows"]
        for table_name, table_contract in USER_TABLES.items()
    }
    assert foreign_key_violations == []


def test_clear_data_keeps_recovery_metadata_and_id_sequences():
    connection = migrations.connect_database()

    try:
        seed_recovery_state(connection)
    finally:
        connection.close()

    assert clear_database() is True

    connection = migrations.connect_database()

    try:
        user_rows = read_user_rows(connection)
        migration_rows = read_migration_rows(connection)
        sequences = dict(
            connection.execute(
                """
                SELECT name, seq
                FROM sqlite_sequence
                WHERE name IN (
                    'accounts',
                    'category_groups',
                    'categories',
                    'transactions',
                    'account_transfers'
                )
                ORDER BY name
                """
            ).fetchall()
        )
    finally:
        connection.close()

    assert user_rows == {
        table_name: []
        for table_name in USER_TABLES
    }
    assert migration_rows == MIGRATION_ROWS
    assert sequences == {
        "accounts": 8,
        "account_transfers": 40,
        "categories": 12,
        "category_groups": 9,
        "transactions": 34,
    }


def test_clear_data_rolls_back_every_table_after_late_failure():
    connection = migrations.connect_database()

    try:
        seed_recovery_state(connection)
        original_rows = read_user_rows(connection)
        connection.execute(
            """
            CREATE TRIGGER prevent_account_clear
            BEFORE DELETE ON accounts
            BEGIN
                SELECT RAISE(ABORT, 'forced clear failure');
            END
            """
        )
        connection.commit()
    finally:
        connection.close()

    assert clear_database() is False

    connection = migrations.connect_database()
    try:
        assert read_user_rows(connection) == original_rows
    finally:
        connection.close()
