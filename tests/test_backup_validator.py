from datetime import datetime, timezone

import pytest

from services.backup_format import (
    BACKUP_FORMAT_VERSION,
    LEGACY_BACKUP_FORMAT_VERSION,
    POSTING_STATUS_BACKUP_FORMAT_VERSION,
    TRANSFER_BACKUP_FORMAT_VERSION,
    create_backup_document,
    serialize_backup_document,
)
from services.backup_validator import (
    BackupValidationError,
    RestorePreview,
    validate_backup_json,
)


def make_valid_document():
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
                {"id": 3, "name": "Banco – Savings"},
                {"id": 8, "name": "Cash / Wallet"},
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
                    "account_id": 3,
                    "amount_centavos": 123456,
                    "category_id": 12,
                    "date_time": "2026-07-01 08:30:00",
                    "notes": None,
                    "posting_status": "temporary",
                },
            ],
            "account_transfers": [
                {
                    "id": 20,
                    "source_account_id": 3,
                    "destination_account_id": 8,
                    "amount_centavos": 10025,
                    "date_time": "2026-07-02 09:15:00",
                    "notes": "Cash-out for Alex",
                    "transfer_kind": "pass_through",
                    "counterparty": "Alex Rivera",
                },
            ],
        },
    )



def convert_to_format(document, format_version):
    document["format_version"] = format_version

    if format_version < POSTING_STATUS_BACKUP_FORMAT_VERSION:
        for transaction in document["records"]["transactions"]:
            transaction.pop("posting_status", None)

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


def validate_document(document):
    return validate_backup_json(
        serialize_backup_document(document)
    )


def add_record(document, table_name, record):
    document["records"][table_name].append(record)
    document["metadata"]["record_counts"][table_name] += 1


def test_valid_backup_returns_restore_preview():
    document = make_valid_document()

    validated_backup = validate_document(document)

    assert validated_backup.document == document
    assert validated_backup.preview == RestorePreview(
        app_version="0.6.0",
        database_version=3,
        exported_at="2026-07-24T12:30:00Z",
        record_counts={
            "accounts": 2,
            "category_groups": 2,
            "categories": 2,
            "transactions": 1,
            "account_transfers": 1,
        },
        total_records=8,
    )


def test_accepts_legacy_backup_with_empty_transfer_set():
    document = convert_to_format(
        make_valid_document(),
        LEGACY_BACKUP_FORMAT_VERSION,
    )

    validated_backup = validate_document(document)

    assert validated_backup.document["format_version"] == (
        BACKUP_FORMAT_VERSION
    )
    assert validated_backup.document["records"]["account_transfers"] == []
    assert validated_backup.preview.record_counts["account_transfers"] == 0
    assert validated_backup.preview.total_records == 7
    assert validated_backup.document["records"]["transactions"] == [
        {
            **document["records"]["transactions"][0],
            "posting_status": "posted",
        }
    ]


def test_accepts_transfer_backup_and_defaults_transactions_to_posted():
    document = convert_to_format(
        make_valid_document(),
        TRANSFER_BACKUP_FORMAT_VERSION,
    )

    validated_backup = validate_document(document)

    assert validated_backup.document["format_version"] == (
        BACKUP_FORMAT_VERSION
    )
    assert validated_backup.document["records"]["transactions"] == [
        {
            **document["records"]["transactions"][0],
            "posting_status": "posted",
        }
    ]
    assert validated_backup.document["records"]["account_transfers"] == [
        {
            **document["records"]["account_transfers"][0],
            "transfer_kind": "internal",
            "counterparty": None,
        }
    ]


def test_accepts_format_3_and_defaults_transfer_metadata_to_internal():
    document = convert_to_format(
        make_valid_document(),
        POSTING_STATUS_BACKUP_FORMAT_VERSION,
    )

    validated_backup = validate_document(document)

    assert validated_backup.document["format_version"] == (
        BACKUP_FORMAT_VERSION
    )
    assert validated_backup.document["records"]["transactions"] == (
        document["records"]["transactions"]
    )
    assert validated_backup.document["records"]["account_transfers"] == [
        {
            **document["records"]["account_transfers"][0],
            "transfer_kind": "internal",
            "counterparty": None,
        }
    ]


@pytest.mark.parametrize("database_version", (4, 5, 6, 7))
def test_accepts_compatible_database_migrations(database_version):
    document = make_valid_document()
    document["metadata"]["database_version"] = database_version

    validated_backup = validate_document(document)

    assert validated_backup.preview.database_version == database_version


def test_rejects_invalid_or_ambiguous_json():
    invalid_documents = (
        "not valid JSON",
        (
            '{"format": "enkryon-backup", '
            '"format": "duplicate"}'
        ),
    )

    for serialized_backup in invalid_documents:
        with pytest.raises(BackupValidationError):
            validate_backup_json(serialized_backup)


def test_rejects_invalid_identity_and_metadata():
    invalid_documents = []

    for path, value in (
        (("format",), "other-backup"),
        (("format_version",), 5),
        (("metadata", "database_version"), 9),
        (("metadata", "app_version"), ""),
        (("metadata", "exported_at"), "July 24, 2026"),
    ):
        document = make_valid_document()
        target = document

        for key in path[:-1]:
            target = target[key]

        target[path[-1]] = value
        invalid_documents.append(document)

    for document in invalid_documents:
        with pytest.raises(BackupValidationError):
            validate_document(document)


def test_rejects_invalid_fields_and_record_counts():
    missing_field = make_valid_document()
    del missing_field["records"]["transactions"][0]["notes"]

    unexpected_field = make_valid_document()
    unexpected_field["records"]["accounts"][0]["balance"] = 123

    wrong_count = make_valid_document()
    wrong_count["metadata"]["record_counts"]["accounts"] = 3

    for document in (
        missing_field,
        unexpected_field,
        wrong_count,
    ):
        with pytest.raises(BackupValidationError):
            validate_document(document)


def test_rejects_invalid_record_values():
    invalid_documents = []

    for table_name, row_number, field_name, value in (
        ("accounts", 0, "id", True),
        ("accounts", 0, "name", " "),
        (
            "category_groups",
            0,
            "transaction_type",
            "transfer",
        ),
        ("categories", 0, "group_id", 0),
        ("transactions", 0, "amount_centavos", 0),
        (
            "transactions",
            0,
            "date_time",
            "2026-02-30 08:30:00",
        ),
        ("transactions", 0, "notes", 42),
        ("transactions", 0, "posting_status", "invalid"),
        ("account_transfers", 0, "amount_centavos", 0),
        (
            "account_transfers",
            0,
            "date_time",
            "2026-02-30 08:30:00",
        ),
        ("account_transfers", 0, "notes", 42),
        ("account_transfers", 0, "transfer_kind", "other"),
        ("account_transfers", 0, "counterparty", " Alex "),
        ("account_transfers", 0, "counterparty", ""),
        ("account_transfers", 0, "counterparty", 42),
    ):
        document = make_valid_document()
        document["records"][table_name][row_number][field_name] = value
        invalid_documents.append(document)

    for document in invalid_documents:
        with pytest.raises(BackupValidationError):
            validate_document(document)


def test_rejects_duplicate_or_conflicting_records():
    invalid_records = (
        (
            "accounts",
            {"id": 8, "name": "banco – savings"},
        ),
        (
            "category_groups",
            {
                "group_id": 10,
                "name": "food",
                "transaction_type": "expense",
            },
        ),
        (
            "categories",
            {
                "category_id": 13,
                "group_id": 4,
                "name": "café",
            },
        ),
        (
            "transactions",
            {
                "id": 15,
                "account_id": 3,
                "amount_centavos": 1,
                "category_id": 6,
                "date_time": "2026-07-02 12:00:00",
                "notes": "",
                "posting_status": "posted",
            },
        ),
        (
            "account_transfers",
            {
                "id": 20,
                "source_account_id": 8,
                "destination_account_id": 3,
                "amount_centavos": 1,
                "date_time": "2026-07-03 12:00:00",
                "notes": "",
                "transfer_kind": "internal",
                "counterparty": None,
            },
        ),
    )

    for table_name, record in invalid_records:
        document = make_valid_document()
        add_record(document, table_name, record)

        with pytest.raises(BackupValidationError):
            validate_document(document)


def test_rejects_missing_parent_records():
    for table_name, row_number, field_name in (
        ("categories", 0, "group_id"),
        ("transactions", 0, "account_id"),
        ("transactions", 0, "category_id"),
        ("account_transfers", 0, "source_account_id"),
        ("account_transfers", 0, "destination_account_id"),
    ):
        document = make_valid_document()
        document["records"][table_name][row_number][field_name] = 999

        with pytest.raises(BackupValidationError):
            validate_document(document)


def test_rejects_transfer_between_same_account():
    document = make_valid_document()
    document["records"]["account_transfers"][0][
        "destination_account_id"
    ] = 3

    with pytest.raises(BackupValidationError):
        validate_document(document)
