# Temporary Transaction Contract

This document locks the product, persistence, calculation, recovery, and
integration rules for Enkryon v1.2.0 temporary transactions before migration
6 or feature code is implemented.

## Release Baseline

- Development starts from the released `v1.1.0` source baseline.
- The verified Windows baseline contains `637` passing tests with `83%` total
  branch coverage on Python `3.13.14`.
- Development occurs on the `update-2-temporary-transactions` branch.
- Database migrations 1 through 5 are released history and must not be edited,
  deleted, or reordered.
- Backup formats 1 and 2 remain supported compatibility history.
- Temporary transactions will be introduced by migration 6 and backup format
  3.

## Posting Status

A transaction keeps its existing income or expense type and gains one explicit
posting status:

- `posted` means the transaction is financially effective;
- `temporary` means the transaction is planned, pending, or provisional and is
  not yet financially effective.

Every transaction that exists before migration 6 becomes `posted`. Unknown or
blank posting-status values are invalid.

## Temporary Record Fields

A temporary transaction uses the same core fields as an existing transaction:

- one account;
- one income or expense category;
- one positive amount stored as integer centavos;
- a date and time using Enkryon's supported database format; and
- optional notes.

Temporary records remain normal transaction identities. They must not be
copied into a second table or duplicated when they are posted.

## Financial Invariants

A temporary transaction is fully non-posting. Until explicit posting, it must
not change:

- the selected account balance;
- total Income or Expenses;
- category or category-group totals;
- net cash flow; or
- statistical financial aggregates.

Temporary records may expose a separate count or face-value context, but that
context must be clearly labeled non-posting and must never be mixed into posted
totals. All stored and calculated money remains integer centavos.

## Lifecycle and Atomic Posting

- A user can save, view, search, filter, edit, delete, and restore a temporary
  transaction through the existing transaction and undo patterns.
- Posting converts the existing record from `temporary` to `posted` in one atomic
  database operation.
- Successful posting immediately applies the exact account, Income or Expense,
  and category effects of the transaction.
- A failed posting operation leaves the record temporary and leaves every
  posted total unchanged.
- A repeated attempt to post an already-posted transaction must be rejected
  without changing the record or any total.
- The first release does not auto-post, auto-expire, or silently remove
  temporary transactions.

## Activity History and Filters

- Temporary transactions appear in Dashboard recent activity and unified
  Activity History.
- Each temporary record has a visible `Temporary` text label and a
  non-color-only status treatment.
- Search includes temporary notes, account names, category-group names, and
  category names.
- The `Temporary` activity filter returns temporary income and expense records.
- Existing `Income` and `Expense` activity filters return posted records only.
- Account, category-group, category, date, and search filters apply to both
  posted and temporary records when their activity type is eligible.
- Newest-first ordering continues to use the record ID as a stable secondary
  key.

## Relationship Safety

- An account referenced by a posted or temporary transaction cannot be deleted.
- A category or category group referenced by a posted or temporary transaction
  remains protected by the existing deletion rules.
- Editing a temporary record must validate its relationships without applying
  any posted financial effect.

## Persistence Direction

Migration 6 extends the existing `transactions` table with a constrained
`posting_status` column whose default is `posted`. Repository balance and total
queries must explicitly include posted transactions only, while activity
queries continue to include both statuses.

The 10,000-record query-plan regression justifies one composite index named
`transactions_posting_status_history_index` on `posting_status`, newest-first
`date_time`, and newest-first `id`. It supports status-filtered Activity History
without a full transaction scan or a temporary ordering table. Account- or
category-specific status indexes remain deferred until a focused filter
combination proves they are necessary.

Migration repeat runs, rollback behavior, legacy upgrades, invalid-status
rejection, stable ordering, exact index shape, and unchanged legacy totals all
require automated coverage.

## Backup and Recovery

- Backup format 3 preserves each transaction's posting status.
- Format-1 and format-2 transactions restore as `posted`.
- Replacement restore validates posting status before changing current data.
- Malformed posting status, relationship, count, or integrity failures roll
  back the complete restore.
- Clear All Data, backup preview, replacement restore, sequence restoration,
  and relaunch checks include temporary records.

## Carried Release Exception

The official physical-device in-place upgrade from `v1.0.0` to `v1.1.0` was
waived by the release owner. Automated migration coverage passed, but that
Android upgrade is not recorded as verified.

The exception is carried into Update 2. Users must export a backup before an
upgrade until the missing official test is closed. The v1.2.0 release gate must
still verify an official `v1.1.0` to `v1.2.0` in-place upgrade with controlled
posted and temporary records and exact totals.

## Completion Evidence Required

Implementation must prove default-posted legacy upgrades, invalid-status
constraints, temporary exclusion from every posted calculation, atomic
posting, failure rollback, repeated-post protection, relationship safety,
unified activity behavior, format-1/2/3 recovery, large-history performance,
full regression, and Android clean-install and upgrade behavior.

The weighted checkpoint evidence is maintained in
`docs/audits/update-2-temporary-transactions-verification.md`.
