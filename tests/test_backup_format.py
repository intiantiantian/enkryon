import json
from datetime import datetime, timedelta, timezone

from services.backup_format import (
    BACKUP_FORMAT,
    BACKUP_FORMAT_VERSION,
    create_backup_document,
    serialize_backup_document,
)


def make_records():
    return {
        "accounts": [
            {"id": 3, "name": "Banco – Savings"},
        ],
        "category_groups": [
            {
                "group_id": 4,
                "name": "Food",
                "transaction_type": "expense",
            },
        ],
        "categories": [
            {
                "category_id": 6,
                "group_id": 4,
                "name": "Café",
            },
        ],
        "transactions": [
            {
                "id": 15,
                "account_id": 3,
                "amount_centavos": 123456,
                "category_id": 6,
                "date_time": "2026-07-01 08:30:00",
                "notes": None,
            },
        ],
    }


def test_create_backup_document_defines_versioned_metadata():
    records = make_records()

    document = create_backup_document(
        app_version="0.6.0",
        database_version=3,
        exported_at=datetime(
            2026,
            7,
            24,
            20,
            30,
            tzinfo=timezone(timedelta(hours=8)),
        ),
        records=records,
    )

    assert document == {
        "format": BACKUP_FORMAT,
        "format_version": BACKUP_FORMAT_VERSION,
        "metadata": {
            "app_version": "0.6.0",
            "database_version": 3,
            "exported_at": "2026-07-24T12:30:00Z",
            "record_counts": {
                "accounts": 1,
                "category_groups": 1,
                "categories": 1,
                "transactions": 1,
            },
        },
        "records": records,
    }


def test_create_backup_document_counts_empty_tables():
    records = {
        "accounts": [],
        "category_groups": [],
        "categories": [],
        "transactions": [],
    }

    document = create_backup_document(
        app_version="0.6.0",
        database_version=3,
        exported_at=datetime(
            2026,
            7,
            24,
            tzinfo=timezone.utc,
        ),
        records=records,
    )

    assert document["metadata"]["record_counts"] == {
        "accounts": 0,
        "category_groups": 0,
        "categories": 0,
        "transactions": 0,
    }


def test_serialize_backup_document_keeps_unicode_and_null_values():
    document = create_backup_document(
        app_version="0.6.0",
        database_version=3,
        exported_at=datetime(
            2026,
            7,
            24,
            tzinfo=timezone.utc,
        ),
        records=make_records(),
    )

    serialized_document = serialize_backup_document(document)

    assert "Banco – Savings" in serialized_document
    assert "Café" in serialized_document
    assert serialized_document.endswith("\n")
    assert json.loads(serialized_document) == document
