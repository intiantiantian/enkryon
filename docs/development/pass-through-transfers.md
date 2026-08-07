# Pass-through Transfer Contract

This document defines the Enkryon v1.3.0 Pass-through model.

The key rule is strict: a Pass-through represents one complete counterparty
exchange and has zero balance effect on every participating user account. It is
also excluded from Income, Expenses, categories, and posted net cash flow.

## Release Baseline

- Development starts from released `v1.2.0`.
- Migrations 1 through 6 are released history and remain unchanged.
- Migration 7 adds `transfer_kind` and optional counterparty.
- Migration 8 is superseded development history that introduced temporary
  `pass_through_movements`.
- Migration 9 removes those temporary movement artifacts and locks the final
  balance-neutral model.
- Formats 1 through 3 remain supported compatibility history.
- Backup format 4 remains the v1.3.0 backup format.

## Product Meaning

A Pass-through is a completed cash-out or money-forwarding exchange for another
person. It is neither earned Income nor spending, and it is not an Internal
Transfer of the user's own money.

Canonical example:

- the user starts with `3,000` in Bank and `9,000` in Cash;
- a friend sends `1,000` into Bank, making Bank `4,000`;
- the user moves that same `1,000` from Bank to Cash, returning Bank to `3,000`
  and making Cash `10,000`;
- the user gives the friend `1,000` from Cash, returning Cash to `9,000`;
- Enkryon stores one Pass-through record for the completed exchange.

The recorded Pass-through therefore leaves both participating account balances
exactly where they started.

For the stored parent, `source_account_id` means the account the counterparty
was paid from and `destination_account_id` means the account that received the
counterparty's matching funds. These roles support history, search, filtering,
and understandable UI copy. They do not create ledger balance effects.

`internal` means the ordinary first-class Account Transfer introduced in
v1.1.0. `pass_through` identifies the cash-out/money-forwarding parent.
Every transfer that exists before migration 7 becomes `internal`.

## Financial Invariants

```text
Pass-through source account balance change = 0
Pass-through destination account balance change = 0
Pass-through all-account balance change = 0
Income change = 0
Expenses change = 0
category-total change = 0
posted net-cash-flow change = 0
```

Creating, editing, deleting, undo-restoring, backup-restoring, or migrating a
Pass-through must never change either participating account balance.

Internal Transfers retain their released behavior: source `-P`, destination
`+P`, and all-account net change `0`.

The principal is never represented as an Income/Expense pair. A real service
charge or fee is recorded separately as a normal posted Expense. All stored
money remains integer centavos.

## Persistence

A Pass-through is persisted as one `account_transfers` row with
`transfer_kind = 'pass_through'`, the two participating account references,
positive integer-centavo principal, date/time, optional notes, and optional
counterparty.

The temporary development `pass_through_movements` table and its triggers are
removed by migration 9. Balance calculation ignores Pass-through parents
entirely.

## Activity, Search, and Filters

The primary Transfer filter includes Internal and Pass-through activity.
Advanced filters distinguish the two kinds. Income, Expense, and Pending
meanings remain unchanged. Search includes counterparty, notes, and both
participating account names. Stable newest-first ordering remains
`date_time DESC, id DESC`.

Visible Pass-through wording uses roles such as `PAID FROM` and
`RECEIVED INTO`, while guidance explicitly states that the complete exchange
does not change either account balance.

## Backup and Recovery

Backup format 4 preserves `transfer_kind`, the two account references, amount,
date/time, notes, and optional counterparty. No derived movement rows are
required. Formats 1 through 3 remain supported and normalize older transfers to
`internal`.

## First-release Exclusions

Partial settlement, unequal principal exchanges, loans, receivables, split
counterparties, multi-leg exchanges, and automatic fee inference remain outside
v1.3.0.
