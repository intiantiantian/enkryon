# Database Architecture

Enkryon uses SQLite for offline local persistence. Repository modules own
database access so screens do not contain raw SQL.

## Database Location

At runtime, the database is stored as `database.db` inside Kivy's
`App.user_data_dir`.

On Windows, the current location is:

```text
%APPDATA%\enkryon\database.db
```

Android uses the corresponding application-specific user-data directory.
The database is not stored inside the source tree or packaged in the APK.

## Connections

`database/connection.py` creates SQLite connections using the path from
`database/path.py`.

Every application connection enables foreign-key enforcement:

```sql
PRAGMA foreign_keys = ON;
```

This prevents transactions and categories from silently referencing
records that do not exist.

## Database Startup

`database/schema.py` is the application entry point for database setup.
It calls the migration runner rather than creating tables independently.

The initial schema creates tables in dependency order:

1. Accounts
2. Category groups
3. Categories
4. Transactions

## Versioned Migrations

`database/migrations.py` contains the ordered migration history.
The `schema_migrations` table records each applied version and name.

The current migrations are:

| Version | Name | Purpose |
|---:|---|---|
| 1 | `initial_schema` | Create the original tables in dependency order. |
| 2 | `transactions_amount_centavos` | Convert legacy decimal amounts to integer centavos. |
| 3 | `validation_constraints` | Add transaction, name, type, and date/time rules. |

The runner applies all pending migrations inside one SQLite transaction.
If any migration fails, the complete attempt is rolled back. Running the
migration runner again skips versions that are already recorded.

The runner also rejects unknown migration versions or a recorded version
whose name does not match the application definition.

## Monetary Values

Transactions store money in the `amount_centavos INTEGER` column.

Examples:

| Peso value | Stored centavos |
|---:|---:|
| `0.01` | `1` |
| `10.20` | `1020` |
| `1234.56` | `123456` |

Integer centavos prevent binary floating-point rounding from affecting
saved values, totals, expenses, income, or balances.

`utils/money.py` owns conversion and display formatting. New database or
service code must not convert financial values back to `float`.

## Database Rules

The current schema enforces these core rules:

- Transaction amounts must be positive integer centavos.
- Transaction date/time values must use the supported valid format.
- Accounts, category groups, and categories require trimmed, non-empty
  names.
- Account names are unique after normalization.
- Category-group names are unique within their transaction type.
- Category names follow the application's normalized duplicate rules.
- Category-group transaction types must be `income` or `expense`.
- Foreign-key relationships must reference existing records.

Application validation should provide friendly messages, while database
rules remain the final protection against invalid stored data.

## Legacy Upgrade Verification

`tests/fixtures/enkryon_v0_3_0.db` preserves the database structure used
before Phase 2. Its transactions use the legacy `amount REAL` column and
it has no migration-history table.

Migration tests copy the fixture to a temporary directory before upgrading
it. The committed historical database must never be migrated in place.

The upgrade test verifies:

- all three migrations are recorded once;
- transaction IDs and record counts are preserved;
- amounts convert to exact centavos;
- income, expense, and balance totals remain correct;
- foreign-key relationships remain valid; and
- running the migrations again does not change the data.

## Adding a Future Migration

When the schema changes:

1. Add a new migration function without editing an already released
   migration.
2. Append a unique, increasing version and descriptive name to
   `MIGRATIONS`.
3. Preserve existing IDs, relationships, and financial totals.
4. Make failures raise an exception so the runner can roll back.
5. Add success, repeat-run, and rollback tests.
6. Add or update a real older-version fixture when compatibility changes.
7. Verify the upgrade on Android before release.

Never delete or reorder a migration that may already exist in a user's
database.

## Android Platform Backup Policy

Enkryon disables Android platform cloud backup through
`android.allow_backup = False` in `buildozer.spec`.

The runtime database contains private financial records. Generic
file-based backup could copy and later restore the database without
Enkryon validating its schema version, application version, record
counts, or financial totals.

This policy remains in effect after Phase 7:

- Enkryon does not opt into Android cloud backup.
- No custom Android backup-rules file is configured.
- User-controlled backup documents are handled separately from the private
  runtime database.
- Android release verification must continue confirming that the generated
  manifest contains `android:allowBackup="false"`.

## User-Controlled Backup and Restore

Phase 7 introduced versioned JSON backup documents containing application and
database versions, export metadata, record counts, and the account, category
group, category, and transaction records needed for recovery.

Before restore begins, the complete document is validated for supported
versions, structure, field values, record counts, IDs, uniqueness, and
relationships. Invalid or incompatible documents cannot modify the current
database.

Confirmed restore deliberately replaces current application data inside one
SQLite transaction:

1. Existing records are removed in reverse dependency order.
2. Backup records are inserted in dependency order while preserving IDs.
3. SQLite ID sequences are restored consistently with the imported records.
4. Foreign-key integrity is checked before the transaction commits.
5. Any failure rolls back the complete replacement.

Android uses the system document picker for backup export and import without
requesting broad storage permission.
Restore in `v0.7.0` does not merge records; backup merging is deferred until
after statistics.
