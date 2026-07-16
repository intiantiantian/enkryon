from .account_repository import create_accounts_table
from .category_group_repository import create_category_groups_table
from .category_repository import create_categories_table
from .connection import connect_database
from .transaction_repository import create_transactions_table


class MigrationError(RuntimeError):
    pass


def create_initial_schema(connection):
    create_accounts_table(connection)
    create_category_groups_table(connection)
    create_categories_table(connection)
    create_transactions_table(connection)


MIGRATIONS = (
    (1, "initial_schema", create_initial_schema),
)


def _validate_migrations(configured_migrations):
    versions = [
        version
        for version, _name, _migration in configured_migrations
    ]

    if (
        versions != sorted(versions)
        or len(versions) != len(set(versions))
        or any(version < 1 for version in versions)
    ):
        raise MigrationError(
            "Migrations must have unique, positive versions in ascending order."
        )


def run_migrations():
    configured_migrations = tuple(MIGRATIONS)
    _validate_migrations(configured_migrations)

    connection = connect_database()

    try:
        connection.execute("BEGIN")
        connection.execute('''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        applied_migrations = dict(
            connection.execute(
                '''
                SELECT version, name
                FROM schema_migrations
                ORDER BY version
                '''
            ).fetchall()
        )

        known_versions = {
            version
            for version, _name, _migration in configured_migrations
        }
        unknown_versions = sorted(
            set(applied_migrations) - known_versions
        )

        if unknown_versions:
            raise MigrationError(
                "Database contains unknown migration versions: "
                f"{unknown_versions}"
            )

        for version, name, migration in configured_migrations:
            applied_name = applied_migrations.get(version)

            if applied_name is not None:
                if applied_name != name:
                    raise MigrationError(
                        f"Migration {version} was recorded as "
                        f"{applied_name!r}, expected {name!r}."
                    )

                continue

            migration(connection)
            connection.execute(
                '''
                INSERT INTO schema_migrations (version, name)
                VALUES (?, ?)
                ''',
                (version, name),
            )

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()