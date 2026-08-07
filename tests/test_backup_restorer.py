from datetime import datetime, timezone

import sqlite3
import pytest

from database import migrations
import services.backup_restorer as backup_restorer
from services.backup_format import (
    BACKUP_RECORD_COLUMNS,
    LEGACY_BACKUP_FORMAT_VERSION,
    TRANSFER_BACKUP_FORMAT_VERSION,
    create_backup_document,
    serialize_backup_document,
)
from services.backup_exporter import export_backup_document
from services.backup_restorer import (
    BackupRestoreError,
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
                    "posting_status": "posted",
                },
                {
                    "id": 21,
                    "account_id": 3,
                    "amount_centavos": 1,
                    "category_id": 6,
                    "date_time": "2026-07-02 12:00:00",
                    "notes": "",
                    "posting_status": "temporary",
                },
            ],
            "account_transfers": [
                {
                    "id": 30,
                    "source_account_id": 8,
                    "destination_account_id": 3,
                    "amount_centavos": 10025,
                    "date_time": "2026-07-03 09:15:00",
                    "notes": "Move to wallet",
                },
            ],
        },
    )



def convert_to_format(document, format_version):
    document["format_version"] = format_version

    for transaction in document["records"]["transactions"]:
        transaction.pop("posting_status", None)

    if format_version == LEGACY_BACKUP_FORMAT_VERSION:
        del document["records"]["account_transfers"]
        del document["metadata"]["record_counts"][
            "account_transfers"
        ]

    return document


def seed_current_records():
    connection = migrations.connect_database()

    try:
        connection.executescript(
            """
            INSERT INTO accounts (id, name)
            VALUES
                (1, 'Old account'),
                (2, 'Old destination');

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

            INSERT INTO account_transfers (
                id,
                source_account_id,
                destination_account_id,
                amount_centavos,
                date_time,
                notes
            )
            VALUES (
                1,
                1,
                2,
                250,
                '2026-07-21 12:00:00',
                'Old transfer'
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


def read_id_sequences():
    connection = migrations.connect_database()

    try:
        placeholders = ", ".join(
            "?"
            for _table_name in BACKUP_RECORD_COLUMNS
        )
        return dict(
            connection.execute(
                f"""
                SELECT name, seq
                FROM sqlite_sequence
                WHERE name IN ({placeholders})
                """,
                tuple(BACKUP_RECORD_COLUMNS),
            ).fetchall()
        )
    finally:
        connection.close()


def set_id_sequences(sequence):
    connection = migrations.connect_database()

    try:
        connection.executemany(
            """
            UPDATE sqlite_sequence
            SET seq = ?
            WHERE name = ?
            """,
            (
                (sequence, table_name)
                for table_name in BACKUP_RECORD_COLUMNS
            ),
        )
        connection.commit()
    finally:
        connection.close()


def insert_next_records():
    connection = migrations.connect_database()

    try:
        account_id = connection.execute(
            """
            INSERT INTO accounts (name)
            VALUES ('Next account')
            """
        ).lastrowid
        group_id = connection.execute(
            """
            INSERT INTO category_groups (
                name,
                transaction_type
            )
            VALUES ('Other income', 'income')
            """
        ).lastrowid
        category_id = connection.execute(
            """
            INSERT INTO categories (group_id, name)
            VALUES (?, 'Bonus')
            """,
            (group_id,),
        ).lastrowid
        transaction_id = connection.execute(
            """
            INSERT INTO transactions (
                account_id,
                amount_centavos,
                category_id,
                date_time,
                notes
            )
            VALUES (
                ?,
                1,
                ?,
                '2026-07-03 12:00:00',
                NULL
            )
            """,
            (account_id, category_id),
        ).lastrowid
        transfer_id = connection.execute(
            """
            INSERT INTO account_transfers (
                source_account_id,
                destination_account_id,
                amount_centavos,
                date_time,
                notes
            )
            VALUES (
                3,
                8,
                1,
                '2026-07-04 12:00:00',
                NULL
            )
            """
        ).lastrowid
        connection.commit()

        return (
            account_id,
            group_id,
            category_id,
            transaction_id,
            transfer_id,
        )
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
        (4, "transaction_history_indexes"),
        (5, "account_transfers"),
        (6, "transaction_posting_status"),
        (7, "account_transfer_kinds"),
    ]


def test_restore_legacy_backup_replaces_transfers_with_empty_set():
    seed_current_records()
    document = convert_to_format(
        make_backup_document(),
        LEGACY_BACKUP_FORMAT_VERSION,
    )

    restore_backup_json(serialize_backup_document(document))

    restored_records = read_current_records()
    assert restored_records["account_transfers"] == []
    assert restored_records["transactions"] == [
        {
            **transaction,
            "posting_status": "posted",
        }
        for transaction in document["records"]["transactions"]
    ]


def test_restore_transfer_backup_defaults_transactions_to_posted():
    seed_current_records()
    document = convert_to_format(
        make_backup_document(),
        TRANSFER_BACKUP_FORMAT_VERSION,
    )

    restore_backup_json(serialize_backup_document(document))

    restored_records = read_current_records()
    assert restored_records["account_transfers"] == (
        document["records"]["account_transfers"]
    )
    assert restored_records["transactions"] == [
        {
            **transaction,
            "posting_status": "posted",
        }
        for transaction in document["records"]["transactions"]
    ]


def test_current_backup_round_trip_preserves_posting_status_and_transfers():
    seed_current_records()
    original_records = read_current_records()
    document = export_backup_document(
        app_version="1.1.0",
        exported_at=datetime(
            2026,
            8,
            4,
            12,
            30,
            tzinfo=timezone.utc,
        ),
    )

    connection = migrations.connect_database()
    try:
        connection.execute("DELETE FROM account_transfers")
        connection.execute("DELETE FROM transactions")
        connection.execute("DELETE FROM categories")
        connection.execute("DELETE FROM category_groups")
        connection.execute("DELETE FROM accounts")
        connection.commit()
    finally:
        connection.close()

    restore_backup_json(serialize_backup_document(document))

    assert read_current_records() == original_records


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


def test_restore_normalizes_autoincrement_sequences():
    seed_current_records()
    set_id_sequences(100)
    validated_backup = validate_backup_document(
        make_backup_document()
    )

    restore_validated_backup(validated_backup)

    assert read_id_sequences() == {
        "accounts": 8,
        "category_groups": 9,
        "categories": 12,
        "transactions": 21,
        "account_transfers": 30,
    }
    assert insert_next_records() == (9, 10, 13, 22, 31)


def test_restore_rolls_back_data_and_sequences_after_late_failure(
    monkeypatch,
):
    seed_current_records()
    set_id_sequences(100)
    original_records = read_current_records()
    original_sequences = read_id_sequences()
    validated_backup = validate_backup_document(
        make_backup_document()
    )

    def fail_verification(_connection, _records):
        raise sqlite3.OperationalError(
            "forced verification failure"
        )

    monkeypatch.setattr(
        backup_restorer,
        "_verify_restored_records",
        fail_verification,
    )

    with pytest.raises(BackupRestoreError):
        restore_validated_backup(validated_backup)

    assert read_current_records() == original_records
    assert read_id_sequences() == original_sequences


def test_restore_rolls_back_when_stored_records_do_not_match(
    monkeypatch,
):
    seed_current_records()
    original_records = read_current_records()
    original_replace = backup_restorer._replace_user_records
    validated_backup = validate_backup_document(
        make_backup_document()
    )

    def replace_with_changed_record(connection, records):
        original_replace(connection, records)
        connection.execute(
            """
            UPDATE accounts
            SET name = 'Changed after insertion'
            WHERE id = 3
            """
        )

    monkeypatch.setattr(
        backup_restorer,
        "_replace_user_records",
        replace_with_changed_record,
    )

    with pytest.raises(BackupRestoreError, match="verify"):
        restore_validated_backup(validated_backup)

    assert read_current_records() == original_records
