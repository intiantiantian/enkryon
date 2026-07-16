import pytest

from database import migrations


def get_migration_rows():
    connection = migrations.connect_database()

    try:
        return connection.execute(
            '''
            SELECT version, name
            FROM schema_migrations
            ORDER BY version
            '''
        ).fetchall()
    finally:
        connection.close()


def test_initial_schema_uses_dependency_order(monkeypatch):
    calls = []
    connection = object()

    monkeypatch.setattr(
        migrations,
        "create_accounts_table",
        lambda shared_connection: calls.append(
            ("accounts", shared_connection)
        ),
    )
    monkeypatch.setattr(
        migrations,
        "create_category_groups_table",
        lambda shared_connection: calls.append(
            ("category_groups", shared_connection)
        ),
    )
    monkeypatch.setattr(
        migrations,
        "create_categories_table",
        lambda shared_connection: calls.append(
            ("categories", shared_connection)
        ),
    )
    monkeypatch.setattr(
        migrations,
        "create_transactions_table",
        lambda shared_connection: calls.append(
            ("transactions", shared_connection)
        ),
    )

    migrations.create_initial_schema(connection)

    assert calls == [
        ("accounts", connection),
        ("category_groups", connection),
        ("categories", connection),
        ("transactions", connection),
    ]


def test_run_migrations_is_idempotent():
    migrations.run_migrations()
    migrations.run_migrations()

    assert get_migration_rows() == [
        (1, "initial_schema"),
    ]


def test_failed_migration_is_rolled_back(monkeypatch):
    def failing_migration(connection):
        connection.execute(
            "CREATE TABLE rolled_back_table (id INTEGER)"
        )
        raise RuntimeError("migration failed")

    monkeypatch.setattr(
        migrations,
        "MIGRATIONS",
        migrations.MIGRATIONS
        + ((2, "failing_migration", failing_migration),),
    )

    with pytest.raises(RuntimeError, match="migration failed"):
        migrations.run_migrations()

    connection = migrations.connect_database()

    try:
        migration_record = connection.execute(
            '''
            SELECT version
            FROM schema_migrations
            WHERE version = 2
            '''
        ).fetchone()
        rolled_back_table = connection.execute(
            '''
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'rolled_back_table'
            '''
        ).fetchone()
    finally:
        connection.close()

    assert migration_record is None
    assert rolled_back_table is None