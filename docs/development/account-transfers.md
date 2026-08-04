# Account Transfer Contract

This document records the product, persistence, and integration rules for
Enkryon v1.1.0 account transfers. The implementation is complete; final
release-candidate verification remains the release gate.

## Release Baseline

- The implementation starts from the released `v1.0.0` baseline.
- The verified baseline contains `504` passing tests with `81%` total coverage.
- Development occurs on the `update-1-account-transfers` branch.
- Database migrations 1 through 4 are released history and must not be edited,
  deleted, or reordered.
- Account transfers will be introduced by database migration 5.

## Transfer Record

A transfer is one first-class, atomic record with:

- one source account;
- one different destination account;
- one positive amount stored as integer centavos;
- a date and time using Enkryon's supported database format; and
- optional notes.

A transfer must never be represented as an unrelated expense and income pair.
Creating or updating one must either succeed completely or leave the database
unchanged.

## Validation Rules

- The source and destination accounts must both exist.
- The source and destination accounts must be different.
- The amount must be an integer greater than zero.
- The source account may become negative after a transfer. This matches the
  existing ledger rule that expenses may produce a negative balance.
- Application validation must provide clear user-facing errors, while database
  constraints and foreign keys remain the final protection against invalid
  records.

## Financial Invariants

- An outgoing transfer decreases the source account balance by the exact
  transferred amount.
- An incoming transfer increases the destination account balance by the exact
  transferred amount.
- Across all accounts, a transfer has a net effect of zero.
- Transfers do not increase Income or Expenses.
- Transfers do not affect category or category-group spending totals.
- All monetary calculations remain integer-centavo calculations from storage
  through service results.

## Lifecycle and Account Safety

- Transfers can be created, viewed, edited, and deleted.
- Editing a transfer must update every affected account balance and activity
  view without leaving partial state.
- Deletion uses confirmation and follows Enkryon's existing restore/undo
  behavior where applicable.
- An account referenced by any transfer cannot be deleted.

## Activity History

- Activity history identifies transfer records separately from income and
  expense transactions.
- Each transfer displays its source and destination accounts.
- With a source-account filter active, the amount is shown as outgoing.
- With a destination-account filter active, the amount is shown as incoming.
- Search and filters must support transfer notes, either participating account,
  date range, and transfer activity type.
- Newest-first ordering uses the record ID as a stable secondary key.

## Backup and Recovery

- The v1.1 backup format includes account transfers as first-class records.
- Replacement restore validates transfer fields, relationships, counts, and
  integrity before changing current data.
- Restore preserves transfer IDs and restores SQLite sequences consistently.
- Any transfer restore failure rolls back the complete replacement operation.
- Existing v1.0 backups remain supported and restore with an empty transfer
  collection.

## Implemented Architecture

- `database/transfer_repository.py` owns transfer persistence and queries.
- `services/transfer_services.py` owns transfer validation and workflows.
- `screens/transfer_form_state.py` owns UI-independent form state.
- `screens/transfer.py` and `kv/transfer.kv` coordinate and render the form.
- Unified activity repository, service, record, and widget code combines
  transactions and transfers without changing their financial meaning.

These boundaries follow the existing rule that screens coordinate UI,
services own business workflows, repositories own SQL, and widgets render
reusable presentation components.

## Completion Evidence

Implementation must prove migration safety, database constraints, atomic CRUD,
exact balances, all-account net-zero behavior, income/expense exclusion,
account-deletion protection, activity filtering, old/new backup recovery, full
regression, and clean-install and v1.0.0-to-v1.1.0 Android upgrades.

The focused checkpoint gates cover the persistence, workflow, interface,
balance/history, backup, rollback, and account-safety requirements. The final
verification record is maintained in
`docs/audits/update-1-account-transfers-verification.md`.
