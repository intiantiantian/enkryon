import sqlite3

from database.connection import managed_connection
from services.backup_format import (
    BACKUP_RECORD_COLUMNS,
    BACKUP_TABLES,
)
from services.backup_validator import (
    validate_backup_document,
    validate_backup_json,
)


class BackupRestoreError(RuntimeError):
    pass


def restore_backup_json(serialized_backup):
    validated_backup = validate_backup_json(serialized_backup)
    return restore_validated_backup(validated_backup)


def restore_validated_backup(validated_backup):
    validated_backup = validate_backup_document(
        validated_backup.document
    )

    try:
        with managed_connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            _replace_user_records(
                connection,
                validated_backup.document["records"],
            )
            connection.commit()
    except sqlite3.Error as error:
        raise BackupRestoreError(
            "Enkryon could not restore the selected backup."
        ) from error

    return validated_backup.preview


def _replace_user_records(connection, records):
    for table_name in reversed(BACKUP_TABLES):
        connection.execute(f"DELETE FROM {table_name}")

    for table_name, columns in BACKUP_RECORD_COLUMNS.items():
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
