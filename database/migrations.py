from .account_repository import create_accounts_table
from .category_group_repository import create_category_groups_table
from .category_repository import create_categories_table
from .connection import connect_database
from .transaction_repository import create_transactions_table
from utils.money import pesos_to_centavos


class MigrationError(RuntimeError):
    pass


def add_validation_constraints(connection):
    add_transaction_constraints(connection)
    add_entity_constraints(connection)


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


def add_entity_constraints(connection):
    constraint_violations = {
        "accounts": connection.execute(
            '''
            SELECT id
            FROM accounts
            WHERE length(trim(name)) = 0
               OR name != trim(name)
            '''
        ).fetchall(),
        "category_groups": connection.execute(
            '''
            SELECT group_id
            FROM category_groups
            WHERE length(trim(name)) = 0
               OR name != trim(name)
               OR transaction_type NOT IN ('income', 'expense')
            '''
        ).fetchall(),
        "categories": connection.execute(
            '''
            SELECT category_id
            FROM categories
            WHERE length(trim(name)) = 0
               OR name != trim(name)
            '''
        ).fetchall(),
        "duplicate_accounts": connection.execute(
            '''
            SELECT lower(trim(name))
            FROM accounts
            GROUP BY lower(trim(name))
            HAVING count(*) > 1
            '''
        ).fetchall(),
        "duplicate_groups": connection.execute(
            '''
            SELECT lower(trim(name)), transaction_type
            FROM category_groups
            GROUP BY lower(trim(name)), transaction_type
            HAVING count(*) > 1
            '''
        ).fetchall(),
        "duplicate_categories": connection.execute(
            '''
            SELECT
                lower(trim(categories.name)),
                category_groups.transaction_type
            FROM categories
            INNER JOIN category_groups
                ON categories.group_id = category_groups.group_id
            GROUP BY
                lower(trim(categories.name)),
                category_groups.transaction_type
            HAVING count(*) > 1
            '''
        ).fetchall(),
    }

    active_violations = {
        name: rows
        for name, rows in constraint_violations.items()
        if rows
    }

    if active_violations:
        raise MigrationError(
            "Existing records violate entity constraints: "
            f"{active_violations}"
        )

    connection.execute(
        '''
        CREATE UNIQUE INDEX accounts_normalized_name_unique
        ON accounts (lower(trim(name)))
        '''
    )
    connection.execute(
        '''
        CREATE UNIQUE INDEX category_groups_normalized_name_type_unique
        ON category_groups (
            lower(trim(name)),
            transaction_type
        )
        '''
    )
    connection.execute(
        '''
        CREATE UNIQUE INDEX categories_normalized_name_group_unique
        ON categories (
            group_id,
            lower(trim(name))
        )
        '''
    )

    connection.execute('''
        CREATE TRIGGER validate_accounts_insert
        BEFORE INSERT ON accounts
        FOR EACH ROW
        WHEN length(trim(NEW.name)) = 0
          OR NEW.name != trim(NEW.name)
        BEGIN
            SELECT RAISE(
                ABORT,
                'account name must be trimmed and nonempty'
            );
        END
    ''')
    connection.execute('''
        CREATE TRIGGER validate_accounts_update
        BEFORE UPDATE ON accounts
        FOR EACH ROW
        WHEN length(trim(NEW.name)) = 0
          OR NEW.name != trim(NEW.name)
        BEGIN
            SELECT RAISE(
                ABORT,
                'account name must be trimmed and nonempty'
            );
        END
    ''')

    connection.execute('''
        CREATE TRIGGER validate_category_groups_insert
        BEFORE INSERT ON category_groups
        FOR EACH ROW
        WHEN length(trim(NEW.name)) = 0
          OR NEW.name != trim(NEW.name)
          OR NEW.transaction_type NOT IN ('income', 'expense')
        BEGIN
            SELECT RAISE(
                ABORT,
                'invalid category group'
            );
        END
    ''')
    connection.execute('''
        CREATE TRIGGER validate_category_groups_update
        BEFORE UPDATE ON category_groups
        FOR EACH ROW
        WHEN length(trim(NEW.name)) = 0
          OR NEW.name != trim(NEW.name)
          OR NEW.transaction_type NOT IN ('income', 'expense')
          OR NEW.transaction_type != OLD.transaction_type
        BEGIN
            SELECT RAISE(
                ABORT,
                'invalid category group update'
            );
        END
    ''')

    connection.execute('''
        CREATE TRIGGER validate_categories_insert
        BEFORE INSERT ON categories
        FOR EACH ROW
        BEGIN
            SELECT RAISE(
                ABORT,
                'category name must be trimmed and nonempty'
            )
            WHERE length(trim(NEW.name)) = 0
               OR NEW.name != trim(NEW.name);

            SELECT RAISE(
                ABORT,
                'duplicate category name for transaction type'
            )
            WHERE EXISTS (
                SELECT 1
                FROM categories AS existing_category
                INNER JOIN category_groups AS existing_group
                    ON existing_category.group_id =
                       existing_group.group_id
                INNER JOIN category_groups AS target_group
                    ON target_group.group_id = NEW.group_id
                WHERE lower(trim(existing_category.name)) =
                      lower(trim(NEW.name))
                  AND existing_group.transaction_type =
                      target_group.transaction_type
            );
        END
    ''')
    connection.execute('''
        CREATE TRIGGER validate_categories_update
        BEFORE UPDATE ON categories
        FOR EACH ROW
        BEGIN
            SELECT RAISE(
                ABORT,
                'category name must be trimmed and nonempty'
            )
            WHERE length(trim(NEW.name)) = 0
               OR NEW.name != trim(NEW.name);

            SELECT RAISE(
                ABORT,
                'duplicate category name for transaction type'
            )
            WHERE EXISTS (
                SELECT 1
                FROM categories AS existing_category
                INNER JOIN category_groups AS existing_group
                    ON existing_category.group_id =
                       existing_group.group_id
                INNER JOIN category_groups AS target_group
                    ON target_group.group_id = NEW.group_id
                WHERE existing_category.category_id !=
                      OLD.category_id
                  AND lower(trim(existing_category.name)) =
                      lower(trim(NEW.name))
                  AND existing_group.transaction_type =
                      target_group.transaction_type
            );
        END
    ''')


def add_transaction_constraints(connection):
    invalid_transactions = connection.execute(
        '''
        SELECT id
        FROM transactions
        WHERE typeof(amount_centavos) != 'integer'
           OR amount_centavos <= 0
           OR strftime(
               '%Y-%m-%d %H:%M:%S',
               date_time
           ) IS NULL
           OR date_time != strftime(
               '%Y-%m-%d %H:%M:%S',
               date_time
           )
        ORDER BY id
        '''
    ).fetchall()

    if invalid_transactions:
        invalid_ids = [
            transaction_id
            for transaction_id, in invalid_transactions
        ]
        raise MigrationError(
            "Transactions violate the required amount or datetime "
            f"constraints: {invalid_ids}"
        )

    connection.execute('''
        CREATE TABLE transactions_v3 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            amount_centavos INTEGER NOT NULL
                CHECK (
                    typeof(amount_centavos) = 'integer'
                    AND amount_centavos > 0
                ),
            category_id INTEGER NOT NULL,
            date_time TEXT NOT NULL
                CHECK (
                    strftime(
                        '%Y-%m-%d %H:%M:%S',
                        date_time
                    ) IS NOT NULL
                    AND date_time = strftime(
                        '%Y-%m-%d %H:%M:%S',
                        date_time
                    )
                ),
            notes TEXT,

            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )
    ''')

    connection.execute(
        '''
        INSERT INTO transactions_v3 (
            id,
            account_id,
            amount_centavos,
            category_id,
            date_time,
            notes
        )
        SELECT
            id,
            account_id,
            amount_centavos,
            category_id,
            date_time,
            notes
        FROM transactions
        ORDER BY id
        '''
    )

    source_count = connection.execute(
        "SELECT COUNT(*) FROM transactions"
    ).fetchone()[0]
    migrated_count = connection.execute(
        "SELECT COUNT(*) FROM transactions_v3"
    ).fetchone()[0]

    if migrated_count != source_count:
        raise MigrationError(
            "Transaction count changed while adding constraints."
        )

    foreign_key_violations = connection.execute(
        "PRAGMA foreign_key_check(transactions_v3)"
    ).fetchall()

    if foreign_key_violations:
        raise MigrationError(
            "Foreign-key violations were found while adding "
            "transaction constraints."
        )

    connection.execute("DROP TABLE transactions")
    connection.execute(
        "ALTER TABLE transactions_v3 RENAME TO transactions"
    )


MIGRATIONS = (
    (1, "initial_schema", create_initial_schema),
    (
        2,
        "transactions_amount_centavos",
        migrate_transactions_to_centavos,
    ),
    (
        3,
        "validation_constraints",
        add_validation_constraints,
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