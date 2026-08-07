from datetime import datetime, timezone

import pytest

from database import migrations
from database.settings_repository import clear_database
from database.transaction_repository import (
    get_current_balance_centavos,
    get_total_centavos,
)
from services.backup_exporter import export_backup_document
from services.backup_format import (
    BACKUP_FORMAT_VERSION,
    LEGACY_BACKUP_FORMAT_VERSION,
    POSTING_STATUS_BACKUP_FORMAT_VERSION,
    TRANSFER_BACKUP_FORMAT_VERSION,
    serialize_backup_document,
)
from services.backup_restorer import restore_backup_json
from services.backup_validator import BackupValidationError


EXPORTED_AT = datetime(
    2026,
    8,
    5,
    12,
    0,
    tzinfo=timezone.utc,
)


def seed_mixed_recovery_data():
    connection = migrations.connect_database()

    try:
        connection.executescript(
            """
            INSERT INTO accounts (id, name)
            VALUES
                (3, 'Cash / Wallet'),
                (8, 'Banco Savings');

            INSERT INTO category_groups (
                group_id,
                name,
                transaction_type
            )
            VALUES
                (4, 'Food', 'expense'),
                (9, 'Salary', 'income');

            INSERT INTO categories (
                category_id,
                group_id,
                name
            )
            VALUES
                (6, 4, 'Meals'),
                (12, 9, 'Paycheck');

            INSERT INTO transactions (
                id,
                account_id,
                amount_centavos,
                category_id,
                date_time,
                notes,
                posting_status
            )
            VALUES
                (
                    15,
                    8,
                    100000,
                    12,
                    '2026-08-01 08:30:00',
                    'Posted salary',
                    'posted'
                ),
                (
                    21,
                    8,
                    25000,
                    6,
                    '2026-08-02 12:00:00',
                    'Pending meal budget',
                    'temporary'
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
                30,
                8,
                3,
                20000,
                '2026-08-03 09:15:00',
                'Move to wallet'
            );
            """
        )
        connection.commit()
    finally:
        connection.close()


def read_statuses_and_integrity():
    connection = migrations.connect_database()

    try:
        statuses = connection.execute(
            """
            SELECT id, posting_status
            FROM transactions
            ORDER BY id
            """
        ).fetchall()
        counts = {
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
        foreign_keys = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()
        integrity = connection.execute(
            "PRAGMA integrity_check"
        ).fetchall()
    finally:
        connection.close()

    return statuses, counts, sequences, foreign_keys, integrity


def export_mixed_document():
    seed_mixed_recovery_data()
    return export_backup_document(
        app_version="1.2.0",
        exported_at=EXPORTED_AT,
    )


def convert_to_older_format(document, format_version):
    document["format_version"] = format_version

    if format_version < POSTING_STATUS_BACKUP_FORMAT_VERSION:
        for transaction in document["records"]["transactions"]:
            transaction.pop("posting_status")

    if format_version < BACKUP_FORMAT_VERSION:
        for transfer in document["records"]["account_transfers"]:
            transfer.pop("transfer_kind", None)
            transfer.pop("counterparty", None)

    if format_version == LEGACY_BACKUP_FORMAT_VERSION:
        del document["records"]["account_transfers"]
        del document["metadata"]["record_counts"][
            "account_transfers"
        ]

    return document


def test_format_3_export_preserves_exact_posting_status():
    document = export_mixed_document()

    assert document["format_version"] == BACKUP_FORMAT_VERSION
    assert document["metadata"]["database_version"] == 9
    assert document["metadata"]["record_counts"] == {
        "accounts": 2,
        "category_groups": 2,
        "categories": 2,
        "transactions": 2,
        "account_transfers": 1,
    }
    assert [
        transaction["posting_status"]
        for transaction in document["records"]["transactions"]
    ] == ["posted", "temporary"]


def test_format_3_round_trip_preserves_status_and_financial_totals():
    document = export_mixed_document()

    before_totals = (
        get_total_centavos("income"),
        get_total_centavos("expense"),
        get_current_balance_centavos(8),
        get_current_balance_centavos(3),
        get_current_balance_centavos(),
    )
    assert clear_database() is True

    restore_backup_json(serialize_backup_document(document))

    statuses, counts, _sequences, foreign_keys, integrity = (
        read_statuses_and_integrity()
    )
    assert statuses == [(15, "posted"), (21, "temporary")]
    assert counts == document["metadata"]["record_counts"]
    assert before_totals == (100000, 0, 80000, 20000, 100000)
    assert (
        get_total_centavos("income"),
        get_total_centavos("expense"),
        get_current_balance_centavos(8),
        get_current_balance_centavos(3),
        get_current_balance_centavos(),
    ) == before_totals
    assert foreign_keys == []
    assert integrity == [("ok",)]


@pytest.mark.parametrize(
    "format_version",
    (
        LEGACY_BACKUP_FORMAT_VERSION,
        TRANSFER_BACKUP_FORMAT_VERSION,
    ),
)
def test_older_formats_restore_every_transaction_as_posted(
    format_version,
):
    document = convert_to_older_format(
        export_mixed_document(),
        format_version,
    )
    assert clear_database() is True

    restore_backup_json(serialize_backup_document(document))

    statuses, counts, _sequences, foreign_keys, integrity = (
        read_statuses_and_integrity()
    )
    assert statuses == [(15, "posted"), (21, "posted")]
    assert counts["account_transfers"] == (
        0 if format_version == LEGACY_BACKUP_FORMAT_VERSION else 1
    )
    assert get_total_centavos("income") == 100000
    assert get_total_centavos("expense") == 25000
    assert foreign_keys == []
    assert integrity == [("ok",)]


@pytest.mark.parametrize(
    "posting_status",
    (None, "", "pending", "POSTED"),
)
def test_format_3_rejects_missing_or_invalid_status_before_replace(
    posting_status,
):
    document = export_mixed_document()
    original_state = read_statuses_and_integrity()
    transaction = document["records"]["transactions"][1]

    if posting_status is None:
        del transaction["posting_status"]
    else:
        transaction["posting_status"] = posting_status

    with pytest.raises(BackupValidationError):
        restore_backup_json(serialize_backup_document(document))

    assert read_statuses_and_integrity() == original_state


def test_clear_restore_relaunch_preserves_sequences_and_statuses():
    document = export_mixed_document()
    assert clear_database() is True

    restore_backup_json(serialize_backup_document(document))

    first_read = read_statuses_and_integrity()
    second_read = read_statuses_and_integrity()
    statuses, counts, sequences, foreign_keys, integrity = second_read

    assert first_read == second_read
    assert statuses == [(15, "posted"), (21, "temporary")]
    assert counts == document["metadata"]["record_counts"]
    assert sequences == {
        "accounts": 8,
        "account_transfers": 30,
        "categories": 12,
        "category_groups": 9,
        "transactions": 21,
    }
    assert foreign_keys == []
    assert integrity == [("ok",)]
