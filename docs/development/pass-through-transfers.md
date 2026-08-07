# Pass-through Transfer Contract

This document locks the product, persistence, calculation, activity, recovery,
and compatibility rules for Enkryon v1.3.0 Pass-through Transfers before
migration 7 or feature code is implemented.

## Release Baseline

- Development starts from the released `v1.2.0` source baseline.
- The verified Windows baseline contains `746` passing tests with `83%` total
  branch coverage on Python `3.13.14`.
- Development occurs on the `update-3-pass-through-transfers` branch.
- Database migrations 1 through 6 are released history and must not be edited,
  deleted, or reordered.
- Backup formats 1 through 3 remain supported compatibility history.
- Pass-through Transfers will be introduced by migration 7 and backup format 4.

## Product Meaning

A Pass-through Transfer represents a completed exchange in which value enters
one account owned by the user while the same principal leaves another account
owned by the user. It is not earned Income, spending, a loan, a receivable, or
a Pending Transaction.

The canonical cash-out example is:

- a friend sends `₱1,000.25` to the user's Bank account;
- the user gives that friend `₱1,000.25` from Cash; and
- Enkryon stores one linked Pass-through record with Cash as the outflow leg
  and Bank as the inflow leg.

The source field is the user-owned account whose balance decreases and therefore
represents the account outflow. The destination field is the user-owned account
whose balance increases and therefore represents the account inflow. This stored
source/destination mapping must not be described to the user as though the same
physical money was internally transferred between those accounts.

## Transfer Kind

Pass-through Transfers extend the existing `account_transfers` ledger rather
than creating a second financial subsystem.

Migration 7 adds one constrained transfer kind:

- `internal` means the ordinary first-class Account Transfer introduced in
  v1.1.0; and
- `pass_through` means the completed cash-out or money-forwarding exchange
  defined by this contract.

Every transfer that exists before migration 7 becomes `internal`. Unknown or
blank transfer-kind values are invalid. Ordinary Internal transfers must keep
all v1.2.0 behavior unchanged.

## Record Fields

Both transfer kinds keep the existing fields:

- one source account;
- one different destination account;
- one positive amount stored as exact integer centavos;
- a date and time using Enkryon's supported database format; and
- optional notes.

Pass-through records additionally support one optional `counterparty` text
field. The value is trimmed; blank text normalizes to no counterparty. The
existing Notes field carries any optional purpose or descriptive detail, so
v1.3.0 does not add a separate purpose column.

One record represents one completed equal-principal exchange. Partial
settlement, multiple counterparties, debts, loans, receivables, and multi-leg
exchanges are outside v1.3.0.

## Financial Invariants

For principal amount `P`, source account `S`, and destination account `D`:

```text
balance(S) = balance(S) - P
balance(D) = balance(D) + P
all-account balance change = 0
Income change = 0
Expenses change = 0
category-total change = 0
posted net-cash-flow change = 0
```

The principal must never be represented as an Income/Expense pair. It must not
enter category or category-group totals. All stored and calculated money remains
integer centavos.

A real service charge or fee is not part of the Pass-through principal. The
user records the fee separately as a normal posted Expense, so only that fee
changes Expenses and its selected category totals.

## Validation and Lifecycle

- Source and destination accounts must both exist.
- Source and destination accounts must be different.
- The principal must be greater than zero exact centavos.
- A source account may become negative, matching existing transfer behavior.
- Pass-through records support create, view, edit, delete, and undo-restore.
- Editing changes the one existing record; it does not create compensating
  Income or Expense transactions.
- Failed create, edit, delete, or restore operations leave persisted transfer
  state unchanged.
- Because balances are derived from the transfer ledger, one successful record
  mutation produces both equal-and-opposite account effects together.
- Either participating account remains protected from deletion while referenced
  by either Internal or Pass-through transfers.

## Activity, Search, and Filters

- Dashboard recent activity and Activity History show Pass-through records as
  transfer activity with visible `Pass-through` text, not color alone.
- The primary `Transfer` filter includes both `internal` and `pass_through`
  records.
- Advanced transfer-kind filtering must distinguish `Internal` from
  `Pass-through` without changing the existing Income, Expense, or Pending
  meanings.
- `Income` and `Expense` filters exclude all transfers.
- `Pending` includes only Pending income/expense transactions and excludes all
  transfers.
- `All` includes both transfer kinds together with the existing transaction
  activity kinds.
- Search for Pass-through activity includes counterparty, notes, source account,
  and destination account names.
- Account and inclusive date filters apply to both transfer kinds.
- Stable newest-first ordering remains `date_time DESC, id DESC`.

## Persistence Direction

Migration 7 extends `account_transfers` rather than adding a new ledger. The
planned schema direction is:

```sql
ALTER TABLE account_transfers
ADD COLUMN transfer_kind TEXT NOT NULL DEFAULT 'internal'
CHECK (transfer_kind IN ('internal', 'pass_through'));

ALTER TABLE account_transfers
ADD COLUMN counterparty TEXT;
```

The exact migration implementation may rebuild the table if SQLite constraint
or rollback requirements make that safer, but migrations 1 through 6 must
remain unchanged. Indexes are added only when focused query-plan evidence shows
a need.

## Backup and Recovery

Backup format 4 preserves `transfer_kind` and optional `counterparty` for every
transfer. Formats 1 through 3 remain supported:

- transfers from older supported backups normalize to `internal`;
- absence of `counterparty` normalizes to no counterparty; and
- existing Pending/posting semantics remain unchanged.

Replacement restore continues to validate all relationships and record kinds
before changing current data. Any failure rolls back the complete replacement.

## Controlled Acceptance Example

Starting balances:

```text
Cash = ₱5,000.00
Bank = ₱10,000.00
All accounts = ₱15,000.00
```

After one `₱1,000.25` Pass-through exchange with Cash as outflow and Bank as inflow:

```text
Cash = ₱3,999.75
Bank = ₱11,000.25
All accounts = ₱15,000.00
Income change = ₱0.00
Expenses change = ₱0.00
Category totals change = ₱0.00
Posted net cash flow change = ₱0.00
```

If the exchange also incurs a `₱15.00` service fee, the Pass-through principal
remains `₱1,000.25`; the `₱15.00` is recorded separately as a posted Expense.

## First-release Exclusions

v1.3.0 does not add settlement states, partial fulfillment, loan tracking,
receivables, credit balances, split counterparties, multi-leg exchanges, or
automatic fee inference. Those require separate accounting contracts.


## UI text portability

User-facing Kivy copy should prefer plain text when a decorative symbol is not
required. Pass-through records describe the two linked effects explicitly, such
as `Cash outflow | Bank inflow`, instead of using an arrow or wording that looks
like an Internal Transfer. Activity History uses an ASCII separator for active
filters. The peso symbol remains part of monetary formatting.
