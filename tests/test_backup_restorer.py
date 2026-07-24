from datetime import datetime, timezone

import pytest

from database import migrations
from services.backup_format import (
    BACKUP_RECORD_COLUMNS,
    create_backup_document,
)
from services.backup_restorer import (
    restore_backup_json,
    restore_validated_backup,
)
from services.backup_validator import (
    BackupValidationError,
    validate_backup_document,
)


def make_backup_document():
    return create_backup_document(
        app_version="0.6.0",
        database_version=3,
        exported_at=datetime(
            2026,
            7,
            24,
            12,
            30,
            tzinfo=timezone.utc,
        ),
        records={
            "accounts": [
                {"id": 3, "name": "Cash / Wallet"},
                {"id": 8, "name": "Banco – Savings"},
            ],
            "category_groups": [
                {
                    "group_id": 4,
                    "name": "Food",
                    "transaction_type": "expense",
                },
                {
                    "group_id": 9,
                    "name": "Salary",
                    "transaction_type": "income",
                },
            ],
            "categories": [
                {
                    "category_id": 6,
                    "group_id": 4,
                    "name": "Café",
                },
                {
                    "category_id": 12,
                    "group_id": 9,
                    "name": "Paycheck",
                },
            ],
            "transactions": [
                {
                    "id": 15,
                    "account_id": 8,
                    "amount_centavos": 123456,
                    "category_id": 12,
                    "date_time": "2026-07-01 08:30:00",
                    "notes": None,
                },
                {
                    "id": 21,
                    "account_id": 3,
                    "amount_centavos": 1,
                    "category_id": 6,
                    "date_time": "2026-07-02 12:00:00",
                    "notes": "",
                },
            ],
        },
    )


def seed_current_records():
    connection = migrations.connect_database()

    try:
        connection.executescript(
            """
            INSERT INTO accounts (id, name)
            VALUES (1, 'Old account');

            INSERT INTO category_groups (
                group_id,
                name,
                transaction_type
            )
            VALUES (1, 'Old group', 'expense');

            INSERT INTO categories (
                category_id,
                group_id,
                name
            )
            VALUES (1, 1, 'Old category');

            INSERT INTO transactions (
                id,
                account_id,
                amount_centavos,
                category_id,
                date_time,
                notes
            )
            VALUES (
                1,
                1,
                500,
                1,
                '2026-07-20 12:00:00',
                'Old transaction'
            );
            """
        )
        connection.commit()
    finally:
        connection.close()


def read_current_records():
    connection = migrations.connect_database()

    try:
        records = {}

        for table_name, columns in BACKUP_RECORD_COLUMNS.items():
            column_list = ", ".join(columns)
            primary_key = columns[0]
            rows = connection.execute(
                f"SELECT {column_list} "
                f"FROM {table_name} "
                f"ORDER BY {primary_key}"
            ).fetchall()
            records[table_name] = [
                dict(zip(columns, row))
                for row in rows
            ]

        return records
    finally:
        connection.close()


def read_migration_rows():
    connection = migrations.connect_database()

    try:
        return connection.execute(
            """
            SELECT version, name
            FROM schema_migrations
            ORDER BY version
            """
        ).fetchall()
    finally:
        connection.close()


def test_restore_replaces_user_records_and_keeps_schema_history():
    seed_current_records()
    document = make_backup_document()
    validated_backup = validate_backup_document(document)

    preview = restore_validated_backup(validated_backup)

    assert preview == validated_backup.preview
    assert read_current_records() == document["records"]
    assert read_migration_rows() == [
        (1, "initial_schema"),
        (2, "transactions_amount_centavos"),
        (3, "validation_constraints"),
    ]


def test_restore_revalidates_preview_before_opening_transaction():
    seed_current_records()
    original_records = read_current_records()
    validated_backup = validate_backup_document(
        make_backup_document()
    )
    validated_backup.document["records"]["transactions"][0][
        "account_id"
    ] = 999

    with pytest.raises(BackupValidationError):
        restore_validated_backup(validated_backup)

    assert read_current_records() == original_records


def test_restore_rejects_invalid_json_without_changing_current_data():
    seed_current_records()
    original_records = read_current_records()

    with pytest.raises(BackupValidationError):
        restore_backup_json("not valid JSON")

    assert read_current_records() == original_records
