from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest

from database import migrations
from database.settings_repository import clear_database
from database.transaction_repository import (
    get_current_balance_centavos,
    get_total_centavos,
)
from database.transfer_repository import get_transfers
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
    7,
    12,
    0,
    tzinfo=timezone.utc,
)


def seed_mixed_pass_through_data():
    connection = migrations.connect_database()

    try:
        connection.executescript(
            """
            INSERT INTO accounts (id, name)
            VALUES
                (3, 'Cash'),
                (8, 'Bank');

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
                    500000,
                    12,
                    '2026-08-01 08:30:00',
                    'Bank income',
                    'posted'
                ),
                (
                    16,
                    3,
                    200000,
                    12,
                    '2026-08-01 09:00:00',
                    'Cash income',
                    'posted'
                ),
                (
                    21,
                    8,
                    25000,
                    6,
                    '2026-08-02 12:00:00',
                    'Pending meal',
                    'temporary'
                );

            INSERT INTO account_transfers (
                id,
                source_account_id,
                destination_account_id,
                amount_centavos,
                date_time,
                notes,
                transfer_kind,
                counterparty
            )
            VALUES
                (
                    30,
                    8,
                    3,
                    5000,
                    '2026-08-03 09:15:00',
                    'ATM transfer',
                    'internal',
                    NULL
                ),
                (
                    31,
                    3,
                    8,
                    100025,
                    '2026-08-04 10:30:00',
                    'Cash-out exchange',
                    'pass_through',
                    'Alex Rivera'
                );
            """
        )
        connection.commit()
    finally:
        connection.close()


def export_mixed_document():
    seed_mixed_pass_through_data()
    return export_backup_document(
        app_version="1.3.0-dev",
        exported_at=EXPORTED_AT,
    )


def convert_to_older_format(document, format_version):
    document = deepcopy(document)
    document["format_version"] = format_version

    if format_version < BACKUP_FORMAT_VERSION:
        for transfer in document["records"]["account_transfers"]:
            transfer.pop("transfer_kind", None)
            transfer.pop("counterparty", None)

    if format_version < POSTING_STATUS_BACKUP_FORMAT_VERSION:
        for transaction in document["records"]["transactions"]:
            transaction.pop("posting_status", None)

    if format_version == LEGACY_BACKUP_FORMAT_VERSION:
        del document["records"]["account_transfers"]
        del document["metadata"]["record_counts"][
            "account_transfers"
        ]

    return document


def read_transfer_rows():
    connection = migrations.connect_database()

    try:
        return connection.execute(
            """
            SELECT
                id,
                source_account_id,
                destination_account_id,
                amount_centavos,
                date_time,
                notes,
                transfer_kind,
                counterparty
            FROM account_transfers
            ORDER BY id
            """
        ).fetchall()
    finally:
        connection.close()


def read_recovery_integrity():
    connection = migrations.connect_database()

    try:
        sequence = connection.execute(
            """
            SELECT seq
            FROM sqlite_sequence
            WHERE name = 'account_transfers'
            """
        ).fetchone()
        foreign_keys = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()
        integrity = connection.execute(
            "PRAGMA integrity_check"
        ).fetchall()
        return (
            None if sequence is None else sequence[0],
            foreign_keys,
            integrity,
        )
    finally:
        connection.close()


def financial_snapshot():
    return (
        get_total_centavos("income"),
        get_total_centavos("expense"),
        get_current_balance_centavos(8),
        get_current_balance_centavos(3),
        get_current_balance_centavos(),
    )


def test_format_4_export_preserves_transfer_kind_and_counterparty():
    document = export_mixed_document()

    assert document["format_version"] == BACKUP_FORMAT_VERSION == 4
    assert document["metadata"]["database_version"] == 7
    assert document["metadata"]["record_counts"]["account_transfers"] == 2
    assert document["records"]["account_transfers"] == [
        {
            "id": 30,
            "source_account_id": 8,
            "destination_account_id": 3,
            "amount_centavos": 5000,
            "date_time": "2026-08-03 09:15:00",
            "notes": "ATM transfer",
            "transfer_kind": "internal",
            "counterparty": None,
        },
        {
            "id": 31,
            "source_account_id": 3,
            "destination_account_id": 8,
            "amount_centavos": 100025,
            "date_time": "2026-08-04 10:30:00",
            "notes": "Cash-out exchange",
            "transfer_kind": "pass_through",
            "counterparty": "Alex Rivera",
        },
    ]


def test_format_4_round_trip_preserves_financial_and_transfer_semantics():
    document = export_mixed_document()
    before_financial = financial_snapshot()

    assert before_financial == (700000, 0, 595025, 104975, 700000)
    assert clear_database() is True

    restore_backup_json(serialize_backup_document(document))

    assert financial_snapshot() == before_financial
    transfers = get_transfers()
    assert [transfer.transfer_kind for transfer in transfers] == [
        "pass_through",
        "internal",
    ]
    assert [transfer.counterparty for transfer in transfers] == [
        "Alex Rivera",
        None,
    ]
    sequence, foreign_keys, integrity = read_recovery_integrity()
    assert sequence == 31
    assert foreign_keys == []
    assert integrity == [("ok",)]


@pytest.mark.parametrize(
    ("format_version", "expected_transfer_count", "expected_statuses"),
    (
        (LEGACY_BACKUP_FORMAT_VERSION, 0, ["posted", "posted", "posted"]),
        (TRANSFER_BACKUP_FORMAT_VERSION, 2, ["posted", "posted", "posted"]),
        (
            POSTING_STATUS_BACKUP_FORMAT_VERSION,
            2,
            ["posted", "posted", "temporary"],
        ),
    ),
)
def test_formats_1_through_3_normalize_legacy_transfer_metadata(
    format_version,
    expected_transfer_count,
    expected_statuses,
):
    document = convert_to_older_format(
        export_mixed_document(),
        format_version,
    )
    assert clear_database() is True

    restore_backup_json(serialize_backup_document(document))

    transfers = get_transfers()
    assert len(transfers) == expected_transfer_count
    assert all(transfer.transfer_kind == "internal" for transfer in transfers)
    assert all(transfer.counterparty is None for transfer in transfers)

    connection = migrations.connect_database()
    try:
        statuses = [
            row[0]
            for row in connection.execute(
                """
                SELECT posting_status
                FROM transactions
                ORDER BY id
                """
            ).fetchall()
        ]
    finally:
        connection.close()

    assert statuses == expected_statuses


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        ("transfer_kind", "unknown"),
        ("transfer_kind", "PASS_THROUGH"),
        ("counterparty", " Alex Rivera "),
        ("counterparty", ""),
        ("counterparty", 42),
    ),
)
def test_format_4_rejects_invalid_transfer_metadata_before_replace(
    field_name,
    invalid_value,
):
    document = export_mixed_document()
    original_rows = read_transfer_rows()
    document["records"]["account_transfers"][1][field_name] = invalid_value

    with pytest.raises(BackupValidationError):
        restore_backup_json(serialize_backup_document(document))

    assert read_transfer_rows() == original_rows


def seed_large_transfer_history(size=10_000):
    connection = migrations.connect_database()

    try:
        connection.execute(
            "INSERT INTO accounts (id, name) VALUES (1, 'Cash'), (2, 'Bank')"
        )
        starting_datetime = datetime(2026, 1, 1)
        rows = [
            (
                transfer_id,
                1 if transfer_id % 2 else 2,
                2 if transfer_id % 2 else 1,
                transfer_id,
                (
                    starting_datetime
                    + timedelta(minutes=transfer_id)
                ).strftime("%Y-%m-%d %H:%M:%S"),
                f"Transfer {transfer_id}",
                "pass_through" if transfer_id % 5 == 0 else "internal",
                (
                    f"Person {transfer_id}"
                    if transfer_id % 5 == 0
                    else None
                ),
            )
            for transfer_id in range(1, size + 1)
        ]
        connection.executemany(
            """
            INSERT INTO account_transfers (
                id,
                source_account_id,
                destination_account_id,
                amount_centavos,
                date_time,
                notes,
                transfer_kind,
                counterparty
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()
        connection.execute("ANALYZE")
    finally:
        connection.close()


def test_format_4_round_trip_handles_10000_mixed_transfers():
    seed_large_transfer_history()
    document = export_backup_document(
        app_version="1.3.0-dev",
        exported_at=EXPORTED_AT,
    )

    assert document["metadata"]["record_counts"]["account_transfers"] == 10_000
    assert sum(
        transfer["transfer_kind"] == "pass_through"
        for transfer in document["records"]["account_transfers"]
    ) == 2_000

    assert clear_database() is True
    restore_backup_json(serialize_backup_document(document))

    connection = migrations.connect_database()
    try:
        counts = connection.execute(
            """
            SELECT transfer_kind, COUNT(*)
            FROM account_transfers
            GROUP BY transfer_kind
            ORDER BY transfer_kind
            """
        ).fetchall()
        query_plan = connection.execute(
            """
            EXPLAIN QUERY PLAN
            SELECT id
            FROM account_transfers
            WHERE transfer_kind = 'pass_through'
            ORDER BY date_time DESC, id DESC
            LIMIT 25
            """
        ).fetchall()
    finally:
        connection.close()

    assert counts == [("internal", 8_000), ("pass_through", 2_000)]
    details = " ".join(row[3] for row in query_plan)
    assert "account_transfers_history_order_index" in details
    assert "USE TEMP B-TREE FOR ORDER BY" not in details
