from pathlib import Path
import shutil
import sqlite3

from database import migrations


V0_7_0_DATABASE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "enkryon_v0_7_0.db"
)

EXPECTED_STATE = {
    "accounts": [
        (2, "Phase9 Cash"),
        (9, "Phase9 Savings"),
    ],
    "category_groups": [
        (3, "Phase9 Income", "income"),
        (7, "Phase9 Expense", "expense"),
    ],
    "categories": [
        (5, 3, "Salary"),
        (11, 7, "Food"),
    ],
    "transactions": [
        (
            4,
            2,
            123456,
            5,
            "2026-07-24 08:00:00",
            "P9 v0.7 income",
        ),
        (
            12,
            2,
            1,
            11,
            "2026-07-24 12:30:00",
            "P9 centavo boundary",
        ),
        (
            20,
            9,
            1020,
            11,
            "2026-07-25 09:15:00",
            None,
        ),
    ],
    "sqlite_sequence": [
        ("accounts", 9),
        ("categories", 11),
        ("category_groups", 7),
        ("transactions", 20),
    ],
    "totals": {
        "income": 123456,
        "expense": 1021,
    },
}


def read_database_state(connection):
    return {
        "accounts": connection.execute(
            "SELECT id, name FROM accounts ORDER BY id"
        ).fetchall(),
        "category_groups": connection.execute(
            """
            SELECT group_id, name, transaction_type
            FROM category_groups
            ORDER BY group_id
            """
        ).fetchall(),
        "categories": connection.execute(
            """
            SELECT category_id, group_id, name
            FROM categories
            ORDER BY category_id
            """
        ).fetchall(),
        "transactions": connection.execute(
            """
            SELECT
                id,
                account_id,
                amount_centavos,
                category_id,
                date_time,
                notes
            FROM transactions
            ORDER BY id
            """
        ).fetchall(),
        "sqlite_sequence": connection.execute(
            "SELECT name, seq FROM sqlite_sequence ORDER BY name"
        ).fetchall(),
        "totals": dict(
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
        ),
    }


def test_upgrades_v0_7_0_database_file_without_data_loss(
    tmp_path,
    monkeypatch,
):
    upgraded_database = tmp_path / "upgraded_v0_7_0.db"
    shutil.copyfile(V0_7_0_DATABASE, upgraded_database)

    def connect_upgraded_database():
        connection = sqlite3.connect(upgraded_database)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    connection = connect_upgraded_database()

    try:
        original_migrations = connection.execute(
            """
            SELECT version, name
            FROM schema_migrations
            ORDER BY version
            """
        ).fetchall()
        original_state = read_database_state(connection)
    finally:
        connection.close()

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
        migrated_state = read_database_state(connection)
        foreign_key_violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()
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

    assert original_migrations == [
        (1, "initial_schema"),
        (2, "transactions_amount_centavos"),
        (3, "validation_constraints"),
    ]
    assert original_state == EXPECTED_STATE
    assert migration_rows == [
        (1, "initial_schema"),
        (2, "transactions_amount_centavos"),
        (3, "validation_constraints"),
        (4, "transaction_history_indexes"),
    ]
    assert migrated_state == original_state
    assert migrated_state["totals"]["income"] == 123456
    assert migrated_state["totals"]["expense"] == 1021
    assert (
        migrated_state["totals"]["income"]
        - migrated_state["totals"]["expense"]
        == 122435
    )
    assert foreign_key_violations == []
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
