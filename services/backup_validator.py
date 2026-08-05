import json
import sqlite3
from datetime import datetime
from typing import NamedTuple

from database import migrations
from services.backup_format import (
    BACKUP_FORMAT,
    BACKUP_FORMAT_VERSION,
    BACKUP_RECORD_COLUMNS_BY_VERSION,
    BACKUP_TABLES,
)

SUPPORTED_BACKUP_DATABASE_VERSIONS = frozenset({3, 4, 5, 6})


class BackupValidationError(ValueError):
    pass


class RestorePreview(NamedTuple):
    app_version: str
    database_version: int
    exported_at: str
    record_counts: dict
    total_records: int


class ValidatedBackup(NamedTuple):
    document: dict
    preview: RestorePreview


def _is_positive_integer(value):
    return type(value) is int and value > 0


def _is_trimmed_text(value):
    return (
        type(value) is str
        and bool(value)
        and value == value.strip()
    )


def _is_transaction_type(value):
    return (
        type(value) is str
        and value in {"income", "expense"}
    )


def _is_nullable_text(value):
    return value is None or type(value) is str


def _matches_datetime(value, date_format):
    if type(value) is not str:
        return False

    try:
        parsed_value = datetime.strptime(value, date_format)
    except ValueError:
        return False

    return parsed_value.strftime(date_format) == value


RECORD_VALUE_RULES = {
    "accounts": {
        "id": _is_positive_integer,
        "name": _is_trimmed_text,
    },
    "category_groups": {
        "group_id": _is_positive_integer,
        "name": _is_trimmed_text,
        "transaction_type": _is_transaction_type,
    },
    "categories": {
        "category_id": _is_positive_integer,
        "group_id": _is_positive_integer,
        "name": _is_trimmed_text,
    },
    "transactions": {
        "id": _is_positive_integer,
        "account_id": _is_positive_integer,
        "amount_centavos": _is_positive_integer,
        "category_id": _is_positive_integer,
        "date_time": lambda value: _matches_datetime(
            value,
            "%Y-%m-%d %H:%M:%S",
        ),
        "notes": _is_nullable_text,
    },
    "account_transfers": {
        "id": _is_positive_integer,
        "source_account_id": _is_positive_integer,
        "destination_account_id": _is_positive_integer,
        "amount_centavos": _is_positive_integer,
        "date_time": lambda value: _matches_datetime(
            value,
            "%Y-%m-%d %H:%M:%S",
        ),
        "notes": _is_nullable_text,
    },
}


def validate_backup_json(serialized_backup):
    try:
        document = json.loads(
            serialized_backup,
            object_pairs_hook=_build_json_object,
            parse_constant=_reject_json_constant,
        )
    except BackupValidationError:
        raise
    except (json.JSONDecodeError, TypeError, UnicodeDecodeError) as error:
        raise BackupValidationError(
            "The selected file is not a valid Enkryon backup."
        ) from error

    return validate_backup_document(document)


def validate_backup_document(document):
    _require_exact_keys(
        document,
        ("format", "format_version", "metadata", "records"),
        "backup document",
    )

    if document["format"] != BACKUP_FORMAT:
        raise BackupValidationError(
            "The selected file is not an Enkryon backup."
        )

    format_version = document["format_version"]

    if (
        type(format_version) is not int
        or format_version not in BACKUP_RECORD_COLUMNS_BY_VERSION
    ):
        raise BackupValidationError(
            "This backup format version is not supported."
        )

    metadata = document["metadata"]
    records = document["records"]
    record_columns = BACKUP_RECORD_COLUMNS_BY_VERSION[format_version]
    tables = tuple(record_columns)

    _validate_metadata(metadata, tables)
    _validate_record_shapes(records, record_columns)
    _validate_record_counts(
        metadata["record_counts"],
        records,
        tables,
    )
    _validate_relational_records(records, record_columns)

    normalized_document = _normalize_backup_document(document)
    normalized_metadata = normalized_document["metadata"]
    record_counts = dict(normalized_metadata["record_counts"])
    return ValidatedBackup(
        document=normalized_document,
        preview=RestorePreview(
            app_version=normalized_metadata["app_version"],
            database_version=normalized_metadata["database_version"],
            exported_at=normalized_metadata["exported_at"],
            record_counts=record_counts,
            total_records=sum(record_counts.values()),
        ),
    )


def _build_json_object(pairs):
    value = {}

    for key, item in pairs:
        if key in value:
            raise BackupValidationError(
                f"Backup contains duplicate key {key!r}."
            )

        value[key] = item

    return value


def _reject_json_constant(value):
    raise BackupValidationError(
        f"Backup contains unsupported JSON value {value!r}."
    )


def _require_exact_keys(value, expected_keys, label):
    if type(value) is not dict:
        raise BackupValidationError(
            f"The {label} must be a JSON object."
        )

    if set(value) != set(expected_keys):
        raise BackupValidationError(
            f"The {label} has missing or unexpected fields."
        )


def _validate_metadata(metadata, tables):
    _require_exact_keys(
        metadata,
        (
            "app_version",
            "database_version",
            "exported_at",
            "record_counts",
        ),
        "backup metadata",
    )

    if not _is_trimmed_text(metadata["app_version"]):
        raise BackupValidationError(
            "Backup app version is invalid."
        )

    database_version = metadata["database_version"]

    if (
        type(database_version) is not int
        or database_version
        not in SUPPORTED_BACKUP_DATABASE_VERSIONS
    ):
        raise BackupValidationError(
            "This backup database version is not supported."
        )

    if not _matches_datetime(
        metadata["exported_at"],
        "%Y-%m-%dT%H:%M:%SZ",
    ):
        raise BackupValidationError(
            "Backup export time is invalid."
        )

    record_counts = metadata["record_counts"]
    _require_exact_keys(
        record_counts,
        tables,
        "backup record counts",
    )

    if any(
        type(record_counts[table_name]) is not int
        or record_counts[table_name] < 0
        for table_name in tables
    ):
        raise BackupValidationError(
            "Backup record counts are invalid."
        )


def _validate_record_shapes(records, record_columns):
    _require_exact_keys(
        records,
        tuple(record_columns),
        "backup records",
    )

    for table_name, columns in record_columns.items():
        table_records = records[table_name]

        if type(table_records) is not list:
            raise BackupValidationError(
                f"Backup table {table_name!r} must be a list."
            )

        for row_number, record in enumerate(
            table_records,
            start=1,
        ):
            _require_exact_keys(
                record,
                columns,
                f"{table_name} record {row_number}",
            )

            for field_name, rule in (
                RECORD_VALUE_RULES[table_name].items()
            ):
                if not rule(record[field_name]):
                    raise BackupValidationError(
                        f"{table_name} record {row_number} "
                        f"has invalid {field_name!r}."
                    )


def _validate_record_counts(record_counts, records, tables):
    if any(
        record_counts[table_name] != len(records[table_name])
        for table_name in tables
    ):
        raise BackupValidationError(
            "Backup record counts do not match its records."
        )


def _validate_relational_records(records, record_columns):
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        for _version, _name, migration in migrations.MIGRATIONS:
            migration(connection)

        for table_name, columns in record_columns.items():
            column_list = ", ".join(columns)
            placeholders = ", ".join("?" for _column in columns)
            connection.executemany(
                f"INSERT INTO {table_name} ({column_list}) "
                f"VALUES ({placeholders})",
                (
                    tuple(record[column] for column in columns)
                    for record in records[table_name]
                ),
            )

        if connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall():
            raise BackupValidationError(
                "Backup records have invalid relationships."
            )
    except BackupValidationError:
        raise
    except (sqlite3.Error, OverflowError) as error:
        raise BackupValidationError(
            "Backup records violate database constraints."
        ) from error
    finally:
        connection.close()


def _normalize_backup_document(document):
    if document["format_version"] == BACKUP_FORMAT_VERSION:
        return document

    normalized_records = {
        table_name: [
            dict(record)
            for record in document["records"].get(table_name, ())
        ]
        for table_name in BACKUP_TABLES
    }
    normalized_metadata = dict(document["metadata"])
    normalized_metadata["record_counts"] = {
        table_name: len(normalized_records[table_name])
        for table_name in BACKUP_TABLES
    }

    return {
        "format": document["format"],
        "format_version": BACKUP_FORMAT_VERSION,
        "metadata": normalized_metadata,
        "records": normalized_records,
    }
