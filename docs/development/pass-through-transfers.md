# Pass-through Transfer Contract

This document defines the corrected Enkryon v1.3.0 Pass-through model.

The key rule is strict: a Pass-through parent has zero direct balance effect.
The actual external account effects are persisted as explicit linked movement
records. Only a complete, exact inflow/outflow movement pair may affect account
balances.

## Release Baseline

- Development starts from released `v1.2.0`.
- Migrations 1 through 6 are released history and remain unchanged.
- Migration 7 adds `transfer_kind` and optional counterparty.
- Migration 8 adds `pass_through_movements`.
- Formats 1 through 3 remain supported compatibility history.
- Backup format 4 remains the v1.3.0 backup format.

## Product Meaning

A Pass-through is a completed cash-out or money-forwarding exchange for another
person. It is neither earned Income nor spending.

Canonical example:

- a friend sends `1,000.25` into the user's Bank account;
- the user gives the friend `1,000.25` from Cash;
- Enkryon stores one Pass-through parent;
- Enkryon records an explicit `inflow` of `1,000.25` into Bank; and
- Enkryon records an explicit `outflow` of `1,000.25` from Cash.

The parent itself is not an account movement.

`internal` means the ordinary first-class Account Transfer introduced in
v1.1.0. `pass_through` identifies the cash-out/money-forwarding parent.
Every transfer that exists before migration 7 becomes `internal`.

## Explicit Movement Storage

Every valid Pass-through has exactly one `outflow` and one `inflow` movement.
Both rows store the same positive integer-centavo principal as the parent.
Existing development Pass-through parents are backfilled by migration 8.

## Financial Invariants

```text
Pass-through parent direct balance effect = 0
explicit outflow account change = -P
explicit inflow account change = +P
all-account balance change = 0
Income change = 0
Expenses change = 0
category-total change = 0
posted net-cash-flow change = 0
```

If the parent exists without both valid movement rows, the incomplete pair has
zero balance contribution. The rows must match the parent account roles and
principal exactly. All stored and calculated money remains integer centavos.

The principal is never represented as an Income/Expense pair. A real service
charge or fee is recorded separately as a normal posted Expense.

## Lifecycle

Create, edit, delete, and undo-restore keep the parent and its movement records
atomic. Internal Transfer behavior remains unchanged.

## Activity, Search, and Filters

The primary Transfer filter includes Internal and Pass-through activity.
Advanced filters distinguish the two kinds. Income, Expense, and Pending
meanings remain unchanged. Search includes counterparty, notes, and the two
participating account names. Stable newest-first ordering remains
`date_time DESC, id DESC`.

## Backup and Recovery

Backup format 4 preserves `transfer_kind` and optional counterparty. The explicit
movement pair is deterministic from a validated Pass-through parent and is
reconstructed by migration/restore insertion triggers. Formats 1 through 3
remain supported and normalize older transfers to `internal`.

## Controlled Acceptance Example

A Pass-through parent without movement rows changes no account balance.
With a complete pair for `1,000.25`, Cash outflow is `-1,000.25`, Bank inflow is
`+1,000.25`, and the combined balance is unchanged.

## First-release Exclusions

Partial settlement, unequal legs, loans, receivables, split counterparties,
multi-leg exchanges, and automatic fee inference remain outside v1.3.0.
