from .account_repository import create_accounts_table
from .category_group_repository import create_category_groups_table
from .category_repository import create_categories_table
from .connection import connect_database
from .transaction_repository import create_transactions_table
from utils.money import pesos_to_centavos


class MigrationError(RuntimeError):
    pass


def create_initial_schema(connection):
    create_accounts_table(connection)
    create_category_groups_table(connection)
    create_categories_table(connection)
    create_transactions_table(connection)


def migrate_transactions_to_centavos(connection):
    legacy_transactions = connection.execute(
        '''
        SELECT id, account_id, amount, category_id, date_time, notes
        FROM transactions
        ORDER BY id
        '''
    ).fetchall()

    converted_transactions = []

    for (
        transaction_id,
        account_id,
        amount,
        category_id,
        date_time,
        notes,
    ) in legacy_transactions:
        try:
            amount_centavos = pesos_to_centavos(amount)
        except (ValueError, OverflowError) as error:
            raise MigrationError(
                f"Transaction {transaction_id} with amount "
                f"{amount!r} cannot be converted safely: {error}"
            ) from error

        converted_transactions.append(
            (
                transaction_id,
                account_id,
                amount_centavos,
                category_id,
                date_time,
                notes,
            )
        )

    connection.execute('''
        CREATE TABLE transactions_v2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            amount_centavos INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            date_time TEXT NOT NULL,
            notes TEXT,

            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )
    ''')

    connection.executemany(
        '''
        INSERT INTO transactions_v2 (
            id,
            account_id,
            amount_centavos,
            category_id,
            date_time,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        converted_transactions,
    )

    migrated_count = connection.execute(
        "SELECT COUNT(*) FROM transactions_v2"
    ).fetchone()[0]

    if migrated_count != len(legacy_transactions):
        raise MigrationError(
            "Transaction count changed during centavo migration."
        )

    foreign_key_violations = connection.execute(
        "PRAGMA foreign_key_check(transactions_v2)"
    ).fetchall()

    if foreign_key_violations:
        raise MigrationError(
            "Foreign-key violations were found during centavo migration."
        )

    connection.execute("DROP TABLE transactions")
    connection.execute(
        "ALTER TABLE transactions_v2 RENAME TO transactions"
    )


MIGRATIONS = (
    (1, "initial_schema", create_initial_schema),
    (
        2,
        "transactions_amount_centavos",
        migrate_transactions_to_centavos,
    ),
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