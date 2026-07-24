import json
from datetime import datetime, timezone

BACKUP_FORMAT = "enkryon-backup"
BACKUP_FORMAT_VERSION = 1
BACKUP_RECORD_COLUMNS = {
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
        table_name: list(records[table_name])
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
