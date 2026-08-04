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

Migration 5 adds account transfers after both participating account records
exist.

## Versioned Migrations

`database/migrations.py` contains the ordered migration history.
The `schema_migrations` table records each applied version and name.

The current migrations are:

| Version | Name | Purpose |
|---:|---|---|
| 1 | `initial_schema` | Create the original tables in dependency order. |
| 2 | `transactions_amount_centavos` | Convert legacy decimal amounts to integer centavos. |
| 3 | `validation_constraints` | Add transaction, name, type, and date/time rules. |
| 4 | `transaction_history_indexes` | Add indexed newest-first transaction-history access paths. |
| 5 | `account_transfers` | Add atomic transfer records plus newest-first, outgoing, and incoming indexes. |

The runner applies all pending migrations inside one SQLite transaction.
If any migration fails, the complete attempt is rolled back. Running the
migration runner again skips versions that are already recorded.

The runner also rejects unknown migration versions or a recorded version
whose name does not match the application definition.

## Monetary Values

Transactions and account transfers store money in the
`amount_centavos INTEGER` column.

Examples:

| Peso value | Stored centavos |
|---:|---:|
| `0.01` | `1` |
| `10.20` | `1020` |
| `1234.56` | `123456` |

Integer centavos prevent binary floating-point rounding from affecting
saved values, totals, expenses, income, transfers, or balances.

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
- Transfer source and destination accounts must both exist and must differ.
- Transfer amounts must be positive integer centavos.
- Transfer date/time values must use the supported valid format.

Application validation should provide friendly messages, while database
rules remain the final protection against invalid stored data.

## Legacy Upgrade Verification

`tests/fixtures/enkryon_v0_3_0.db` represents the pre-`v0.4.0`
legacy schema. It stores transaction values in the legacy `amount REAL`
column and has no migration-history table.

`tests/fixtures/enkryon_v0_7_0.db` represents the migration-version-3
schema used by `v0.4.0` through `v0.7.0`. It intentionally has no
transaction-history indexes.

Migration tests copy each fixture to a temporary directory before upgrading
it. The committed historical databases must never be migrated in place.

The upgrade tests verify:

- all applicable migrations are recorded exactly once;
- IDs, records, relationships, notes, dates, and SQLite sequences remain
  unchanged;
- amounts and financial totals remain exact integer-centavo values;
- foreign-key validation succeeds;
- all required transaction-history indexes are created; and
- repeating the migration produces no additional changes.

## Large-History Access

Migration 4 creates three transaction-history indexes for newest-first and
filtered access. Repository queries combine search and filters with bound
parameters, treat wildcard characters literally, include complete selected
dates, and use transaction ID as the stable secondary ordering key.

Phase 9 verified startup, totals, history loading, scrolling, exact search,
date-range and combined filters, saving, deletion, and relaunch persistence
with 10,000 transactions. Query-plan tests confirm index use without relying
on a machine-dependent elapsed-time threshold. Interface virtualization is
documented separately because it changes rendering cost, not database
semantics.

The unified activity repository combines income/expense transactions and
account transfers in SQLite before applying stable newest-first ordering and
limits. Transfer indexes support outgoing and incoming account views. A
selected source account sees a negative transfer effect, a selected
destination sees a positive effect, and the all-accounts transfer contribution
is always zero. Transfers never change Income, Expenses, or category totals.

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

This policy remains in effect for version 1.1:

- Enkryon does not opt into Android cloud backup.
- No custom Android backup-rules file is configured.
- User-controlled backup documents are handled separately from the private
  runtime database.
- Android release verification must continue confirming that the generated
  manifest contains `android:allowBackup="false"`.

## User-Controlled Backup and Restore

Phase 7 introduced versioned JSON backup documents containing application and
database versions, export metadata, record counts, and the account, category
group, category, and transaction records needed for recovery. Version 1.1 uses
backup format 2, which adds `account_transfers` as a fifth record collection.
Compatible format-1 documents from version 1.0 are normalized to an empty
transfer collection before validation and restore.

Before restore begins, the complete document is validated for supported
versions, structure, field values, record counts, IDs, uniqueness, and
relationships. Invalid or incompatible documents cannot modify the current
database.

Confirmed restore deliberately replaces current application data inside one
SQLite transaction:

1. Existing transfers and transactions are removed before their parent
   records in reverse dependency order.
2. Parent records, transactions, and transfers are inserted in dependency
   order while preserving IDs.
3. SQLite ID sequences are restored consistently with the imported records.
4. Foreign-key integrity is checked before the transaction commits.
5. Any failure rolls back the complete replacement.

Android uses the system document picker for backup export and import without
requesting broad storage permission.
Restore in `v0.7.0` does not merge records.
Restore in `v1.0.0` does not merge records either; this replacement-only behavior remains unchanged.
Restore in `v1.1.0` remains replacement-only and is transfer-aware.
Backup merging is deferred until after statistics.
