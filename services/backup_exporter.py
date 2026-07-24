from database.connection import managed_connection
from services.backup_format import (
    BACKUP_RECORD_COLUMNS,
    create_backup_document,
    serialize_backup_document,
)


def read_backup_records(connection):
    records = {}

    for table_name, columns in BACKUP_RECORD_COLUMNS.items():
        selected_columns = ", ".join(columns)
        primary_key = columns[0]
        rows = connection.execute(
            f"SELECT {selected_columns} "
            f"FROM {table_name} "
            f"ORDER BY {primary_key}"
        ).fetchall()
        records[table_name] = [
            dict(zip(columns, row))
            for row in rows
        ]

    return records


def export_backup_document(*, app_version, exported_at=None):
    with managed_connection() as connection:
        connection.execute("BEGIN")
        database_version = connection.execute(
            "SELECT MAX(version) FROM schema_migrations"
        ).fetchone()[0]
        records = read_backup_records(connection)

    return create_backup_document(
        app_version=app_version,
        database_version=database_version,
        records=records,
        exported_at=exported_at,
    )


def export_backup_json(*, app_version, exported_at=None):
    document = export_backup_document(
        app_version=app_version,
        exported_at=exported_at,
    )
    return serialize_backup_document(document)
