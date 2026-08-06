# Pending Transaction Contract

This document locks the product, persistence, calculation, recovery, and
integration rules for Enkryon v1.2.0 Pending Transactions before migration
6 or feature code is implemented.

## Release Baseline

- Development starts from the released `v1.1.0` source baseline.
- The verified Windows baseline contains `637` passing tests with `83%` total
  branch coverage on Python `3.13.14`.
- Development occurs on the `update-2-temporary-transactions` branch.
- Database migrations 1 through 5 are released history and must not be edited,
  deleted, or reordered.
- Backup formats 1 and 2 remain supported compatibility history.
- Pending Transactions will be introduced by migration 6 and backup format
  3.

## Posting Status

A transaction keeps its existing income or expense type and gains one explicit
posting status:

- `posted` means the transaction is financially effective;
- `temporary` means the transaction is planned, pending, or provisional and is
  not yet financially effective.

`temporary` remains the internal database and code value for compatibility. The user-facing product term is **Pending**.

Every transaction that exists before migration 6 becomes `posted`. Unknown or
blank posting-status values are invalid.

## Pending Record Fields

A pending transaction uses the same core fields as an existing transaction:

- one account;
- one income or expense category;
- one positive amount stored as integer centavos;
- a date and time using Enkryon's supported database format; and
- optional notes.

Pending records remain normal transaction identities. They must not be
copied into a second table or duplicated when they are posted.

## Financial Invariants

A pending transaction is fully non-posting. Until explicit posting, it must
not change:

- the selected account balance;
- total Income or Expenses;
- category or category-group totals;
- net cash flow; or
- statistical financial aggregates.

Pending records may expose a separate count or face-value context, but that
context must be clearly labeled non-posting and must never be mixed into posted
totals. All stored and calculated money remains integer centavos.

## Lifecycle and Atomic Posting

- A user can save, view, search, filter, edit, delete, and restore a pending
  transaction through the existing transaction and undo patterns.
- Posting converts the existing record from `temporary` to `posted` in one atomic
  database operation.
- Successful posting immediately applies the exact account, Income or Expense,
  and category effects of the transaction.
- A failed posting operation leaves the record pending and leaves every
  posted total unchanged.
- A repeated attempt to post an already-posted transaction must be rejected
  without changing the record or any total.
- Ordinary save and edit workflows cannot change posting status. New records
  may be created explicitly as posted or temporary; an existing record keeps
  its stored status until the dedicated posting workflow succeeds.
- The dedicated posting service first verifies that the record exists and is
  still pending, then performs a compare-and-set status update. An
  already-posted record is rejected before a second write.
- Delete and undo-restore preserve the complete posting status. Removing and
  restoring a pending record cannot make it financially effective.
- Lookup, posting, deletion, and restoration failures return stable service
  results and leave persisted status and posted totals unchanged.
- The first release does not auto-post, auto-expire, or silently remove
  pending transactions.

## Transaction Form Interface

- The transaction form uses explicit text actions rather than an icon-only save
  control: `Save as Pending` and `Post Transaction`.
- New-record guidance explains that posting changes balances and totals while a
  pending save remains non-posting.
- Editing a pending record shows a visible `PENDING` status label, keeps a
  `Save Pending` action, and offers `Post Transaction`.
- Before posting an edited pending record, the current validated fields are
  saved while the record is still pending. The dedicated compare-and-set
  posting operation runs only after that save succeeds.
- If the posting operation then fails, the edited record remains pending and
  every posted balance and total remains unchanged.
- Editing a posted record shows a visible `POSTED` status label, changes the
  primary action to `Save Changes`, and disables the secondary action with the
  explicit text `Already Posted`. A posted transaction cannot return to
  pending.
- The action group stacks on constrained widths, grows with system font scale,
  and keeps both status and meaning available through text rather than color
  alone.

## Activity History and Filters

- Pending transactions appear in Dashboard recent activity and unified
  Activity History.
- Each pending record has a visible `Pending` text label and a
  non-color-only status treatment.
- Unified Activity records carry posting status into both Dashboard recent
  activity and virtualized Activity History without per-card database reads.
- Pending cards pair a clock icon with explicit `PENDING` text and expose a
  guarded post action. Posted transactions and transfers do not expose that
  action.
- Direct posting requires confirmation that the record becomes financially
  effective immediately and that account balances and totals will update.
- Pending deletion confirmation explicitly states that the record does not
  currently affect financial totals.
- A successful direct post refreshes the Dashboard summary and recent activity
  together, while Activity History refreshes its virtualized list.
- Search includes pending-record notes, account names, category-group names, and
  category names.
- The `All` activity filter combines posted transactions, pending
  transactions, and transfers.
- The `Pending` activity filter returns only pending income and expense records
  and never includes transfers.
- Existing `Income` and `Expense` activity filters return posted records only.
- Posting status is a separate filter dimension, so Pending can combine with
  account, category-group, category, date, and search filters.
- Newest-first ordering continues to use the record ID as a stable secondary
  key, and posting moves the existing record between filter views without
  creating a duplicate.

## Relationship Safety

- An account referenced by a posted or pending transaction cannot be deleted.
- A category or category group referenced by a posted or pending transaction
  remains protected by the existing deletion rules.
- Editing a pending record must validate its relationships without applying
  any posted financial effect.

## Persistence Direction

Migration 6 extends the existing `transactions` table with a constrained
`posting_status` column whose default is `posted`. Repository balance and total
queries explicitly include posted transactions only. Unified activity queries
include both statuses for `All`, apply `posted` for Income and Expense, and
apply `temporary` for Pending.

The 10,000-record query-plan regression justifies one composite index named
`transactions_posting_status_history_index` on `posting_status`, newest-first
`date_time`, and newest-first `id`. It supports status-filtered Activity History
without a full transaction scan or a temporary ordering table. Account- or
category-specific status indexes remain deferred until a focused filter
combination proves they are necessary. The 10,000-record Pending activity
regression confirms that the shared Activity query also uses this index without
a temporary ordering B-tree.

Migration repeat runs, rollback behavior, legacy upgrades, invalid-status
rejection, stable ordering, exact index shape, and unchanged legacy totals all
require automated coverage.

## Backup and Recovery

- Backup format 3 preserves each transaction's posting status as an exact
  transaction field.
- Format-1 and format-2 transactions normalize to `posted` before replacement
  restore because those formats predate posting status.
- Replacement restore validates posting status before changing current data.
- Malformed posting status, relationship, count, or integrity failures roll
  back the complete restore.
- Clear All Data, backup preview, replacement restore, sequence restoration,
  and relaunch checks include pending records.

## Carried Release Exception

The official physical-device in-place upgrade from `v1.0.0` to `v1.1.0` was
waived by the release owner. Automated migration coverage passed, but that
Android upgrade is not recorded as verified.

The exception is carried into Update 2. Users must export a backup before an
upgrade until the missing official test is closed. The v1.2.0 release gate must
still verify an official `v1.1.0` to `v1.2.0` in-place upgrade with controlled
posted and pending records and exact totals.

## Completion Evidence Required

Implementation must prove default-posted legacy upgrades, invalid-status
constraints, pending exclusion from every posted calculation, atomic
posting, failure rollback, repeated-post protection, relationship safety,
unified activity behavior, format-1/2/3 recovery, large-history performance,
full regression, and Android clean-install and upgrade behavior.

The weighted checkpoint evidence is maintained in
`docs/audits/update-2-temporary-transactions-verification.md`.
