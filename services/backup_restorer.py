import sqlite3

from database.connection import managed_connection

from services.backup_exporter import read_backup_records
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
            _normalize_id_sequences(
                connection,
                validated_backup.document["records"],
            )
            _verify_restored_records(
                connection,
                validated_backup.document["records"],
            )
            connection.commit()
    except sqlite3.Error as error:
        raise BackupRestoreError(
            "Enkryon could not restore the selected backup."
        ) from error

    return validated_backup.preview


def _expected_id_sequences(records):
    return {
        table_name: max(
            (
                record[columns[0]]
                for record in records[table_name]
            ),
            default=0,
        )
        for table_name, columns in BACKUP_RECORD_COLUMNS.items()
    }


def _normalize_id_sequences(connection, records):
    for table_name, highest_id in (
        _expected_id_sequences(records).items()
    ):
        connection.execute(
            "DELETE FROM sqlite_sequence WHERE name = ?",
            (table_name,),
        )
        connection.execute(
            """
            INSERT INTO sqlite_sequence (name, seq)
            VALUES (?, ?)
            """,
            (table_name, highest_id),
        )


def _verify_restored_records(connection, records):
    expected_records = {
        table_name: sorted(
            records[table_name],
            key=lambda record: record[columns[0]],
        )
        for table_name, columns in BACKUP_RECORD_COLUMNS.items()
    }
    restored_records = read_backup_records(connection)

    placeholders = ", ".join(
        "?"
        for _table_name in BACKUP_TABLES
    )
    restored_sequences = dict(
        connection.execute(
            f"""
            SELECT name, seq
            FROM sqlite_sequence
            WHERE name IN ({placeholders})
            """,
            BACKUP_TABLES,
        ).fetchall()
    )

    foreign_key_violations = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()
    integrity_result = connection.execute(
        "PRAGMA integrity_check"
    ).fetchall()

    if (
        restored_records != expected_records
        or restored_sequences != _expected_id_sequences(records)
        or foreign_key_violations
        or integrity_result != [("ok",)]
    ):
        raise BackupRestoreError(
            "Enkryon could not verify the restored backup."
        )


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
