import json
from datetime import datetime, timezone

BACKUP_FORMAT = "enkryon-backup"
LEGACY_BACKUP_FORMAT_VERSION = 1
TRANSFER_BACKUP_FORMAT_VERSION = 2
POSTING_STATUS_BACKUP_FORMAT_VERSION = 3
PASS_THROUGH_BACKUP_FORMAT_VERSION = 4
INTEREST_BACKUP_FORMAT_VERSION = 5
BACKUP_FORMAT_VERSION = INTEREST_BACKUP_FORMAT_VERSION
LEGACY_BACKUP_RECORD_COLUMNS = {
    "accounts": (
        "id",
        "name",
    ),
    "category_groups": (
        "group_id",
        "name",
        "transaction_type",
    ),
    "categories": (
        "category_id",
        "group_id",
        "name",
    ),
    "transactions": (
        "id",
        "account_id",
        "amount_centavos",
        "category_id",
        "date_time",
        "notes",
    ),
}
TRANSFER_BACKUP_RECORD_COLUMNS = {
    **LEGACY_BACKUP_RECORD_COLUMNS,
    "account_transfers": (
        "id",
        "source_account_id",
        "destination_account_id",
        "amount_centavos",
        "date_time",
        "notes",
    ),
}
POSTING_STATUS_BACKUP_RECORD_COLUMNS = {
    **TRANSFER_BACKUP_RECORD_COLUMNS,
    "transactions": (
        *LEGACY_BACKUP_RECORD_COLUMNS["transactions"],
        "posting_status",
    ),
}
PASS_THROUGH_BACKUP_RECORD_COLUMNS = {
    **POSTING_STATUS_BACKUP_RECORD_COLUMNS,
    "account_transfers": (
        *TRANSFER_BACKUP_RECORD_COLUMNS["account_transfers"],
        "transfer_kind",
        "counterparty",
    ),
}
INTEREST_BACKUP_RECORD_COLUMNS = {
    **PASS_THROUGH_BACKUP_RECORD_COLUMNS,
    "account_interest_profiles": (
        "id",
        "account_id",
        "annual_rate_micros",
        "day_count_basis",
        "effective_from",
        "enabled",
    ),
    "account_interest_accruals": (
        "id",
        "account_id",
        "interest_profile_id",
        "accrual_date",
        "closing_balance_centavos",
        "annual_rate_micros",
        "day_count_basis",
        "accrued_whole_centavos",
        "accrued_remainder_numerator",
        "status",
        "posted_transaction_id",
    ),
}
BACKUP_RECORD_COLUMNS = INTEREST_BACKUP_RECORD_COLUMNS
BACKUP_RECORD_COLUMNS_BY_VERSION = {
    LEGACY_BACKUP_FORMAT_VERSION: LEGACY_BACKUP_RECORD_COLUMNS,
    TRANSFER_BACKUP_FORMAT_VERSION: TRANSFER_BACKUP_RECORD_COLUMNS,
    POSTING_STATUS_BACKUP_FORMAT_VERSION: POSTING_STATUS_BACKUP_RECORD_COLUMNS,
    PASS_THROUGH_BACKUP_FORMAT_VERSION: PASS_THROUGH_BACKUP_RECORD_COLUMNS,
    INTEREST_BACKUP_FORMAT_VERSION: INTEREST_BACKUP_RECORD_COLUMNS,
}
BACKUP_TABLES = tuple(BACKUP_RECORD_COLUMNS)


def create_backup_document(
    *,
    app_version,
    database_version,
    records,
    exported_at=None,
):
    if exported_at is None:
        exported_at = datetime.now(timezone.utc)

    exported_at = exported_at.astimezone(timezone.utc)
    backup_records = {
        table_name: list(records.get(table_name, ()))
        for table_name in BACKUP_TABLES
    }

    return {
        "format": BACKUP_FORMAT,
        "format_version": BACKUP_FORMAT_VERSION,
        "metadata": {
            "app_version": app_version,
            "database_version": database_version,
            "exported_at": (
                exported_at.isoformat(timespec="seconds")
                .replace("+00:00", "Z")
            ),
            "record_counts": {
                table_name: len(backup_records[table_name])
                for table_name in BACKUP_TABLES
            },
        },
        "records": backup_records,
    }


def serialize_backup_document(document):
    return (
        json.dumps(
            document,
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
