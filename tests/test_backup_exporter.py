import json
from datetime import datetime, timezone

from database import migrations
from services.backup_exporter import (
    export_backup_document,
    export_backup_json,
)
from services.backup_format import BACKUP_TABLES


EXPORTED_AT = datetime(
    2026,
    7,
    24,
    12,
    30,
    tzinfo=timezone.utc,
)


def seed_export_data():
    connection = migrations.connect_database()

    try:
        connection.executescript(
            """
            INSERT INTO accounts (id, name)
            VALUES
                (8, 'Banco – Savings'),
                (3, 'Cash / Wallet');

            INSERT INTO category_groups (
                group_id,
                name,
                transaction_type
            )
            VALUES
                (9, 'Salary', 'income'),
                (4, 'Food', 'expense');

            INSERT INTO categories (
                category_id,
                group_id,
                name
            )
            VALUES
                (12, 9, 'Paycheck'),
                (6, 4, 'Café');

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
                    21,
                    3,
                    1,
                    6,
                    '2026-07-02 12:00:00',
                    '',
                    'temporary'
                ),
                (
                    15,
                    8,
                    123456,
                    12,
                    '2026-07-01 08:30:00',
                    NULL,
                    'posted'
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
            VALUES (
                30,
                8,
                3,
                10025,
                '2026-07-03 09:15:00',
                'Cash-out for Alex',
                'pass_through',
                'Alex Rivera'
            );
            """
        )
        connection.commit()
    finally:
        connection.close()


def test_export_backup_document_reads_exact_relational_rows():
    seed_export_data()

    document = export_backup_document(
        app_version="0.6.0",
        exported_at=EXPORTED_AT,
    )

    assert document["metadata"] == {
        "app_version": "0.6.0",
        "database_version": 9,
        "exported_at": "2026-07-24T12:30:00Z",
        "record_counts": {
            "accounts": 2,
            "category_groups": 2,
            "categories": 2,
            "transactions": 2,
            "account_transfers": 1,
        },
    }
    assert document["records"] == {
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
                "notes": "Cash-out for Alex",
                "transfer_kind": "pass_through",
                "counterparty": "Alex Rivera",
            },
        ],
    }


def test_export_backup_document_includes_empty_tables():
    document = export_backup_document(
        app_version="0.6.0",
        exported_at=EXPORTED_AT,
    )

    assert document["metadata"]["database_version"] == 9
    assert document["metadata"]["record_counts"] == {
        table_name: 0
        for table_name in BACKUP_TABLES
    }
    assert document["records"] == {
        table_name: []
        for table_name in BACKUP_TABLES
    }


def test_export_backup_json_serializes_database_records():
    seed_export_data()

    serialized_backup = export_backup_json(
        app_version="0.6.0",
        exported_at=EXPORTED_AT,
    )
    document = json.loads(serialized_backup)

    assert serialized_backup.endswith("\n")
    assert document["records"]["transactions"][0]["notes"] is None
    assert document["records"]["transactions"][1]["notes"] == ""
    assert document["records"]["transactions"][0][
        "posting_status"
    ] == "posted"
    assert document["records"]["transactions"][1][
        "posting_status"
    ] == "temporary"
    assert document["records"]["account_transfers"] == [
        {
            "id": 30,
            "source_account_id": 8,
            "destination_account_id": 3,
            "amount_centavos": 10025,
            "date_time": "2026-07-03 09:15:00",
            "notes": "Cash-out for Alex",
            "transfer_kind": "pass_through",
            "counterparty": "Alex Rivera",
        }
    ]
