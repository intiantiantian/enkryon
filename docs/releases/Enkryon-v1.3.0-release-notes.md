# Enkryon v1.3.0

Release status: `BALANCE-NEUTRALITY CORRECTION CANDIDATE`

## Correction notice

Publication remains stopped before merge/tag. Device testing exposed that the
previous corrected candidate still changed the two participating account
balances for Pass-through records. That APK and all earlier v1.3.0 Android
approval evidence are superseded.

The final model represents the complete counterparty exchange as one
balance-neutral Pass-through record. Pass-through has zero balance effect on each participating account. Neither participating account balance,
Income, Expenses, category totals, nor posted net cash flow may change.

## Summary

Enkryon 1.3 adds Pass-through Transfers for completed cash-out or
money-forwarding exchanges. A Pass-through stores the account paid from, the
account that received the counterparty's matching funds, exact principal,
date/time, notes, and optional counterparty for history and recovery.

It does not post a ledger balance effect to either account.

## User-visible changes

- Added explicit Internal and Pass-through modes to Transfer Funds.
- Added optional counterparty metadata for Pass-through exchanges.
- Pass-through account roles use `PAID FROM` and `RECEIVED INTO`.
- Guidance states that the complete exchange leaves both account balances
  unchanged.
- Added visible PASS-THROUGH activity treatment on Dashboard and Activity
  History.
- Added searchable counterparty and transfer-kind text.
- Added Advanced Internal and Pass-through filters.
- Added backup format 4 so transfer kind and counterparty survive export,
  replacement restore, and relaunch.

## Financial behavior

```text
Pass-through paid-from account change = 0
Pass-through received-into account change = 0
All-account balance change = 0
Income change = 0
Expenses change = 0
Category-total change = 0
```

Internal Transfers keep their released source-negative/destination-positive
balance behavior. A real service fee remains a separate posted Expense.

## Upgrade and stored data

Migration 7 adds Internal/Pass-through kind and optional counterparty.
Migration 8 remains superseded development history. Migration 9 removes the
temporary Pass-through movement table/triggers and locks the balance-neutral
model. Every transfer that exists before migration 7 becomes Internal. Existing pre-v1.3 transfers therefore remain Internal.

New exports use backup format 4. Compatible formats 1 through 3 remain
restorable and older transfers normalize to Internal.

## Artifact identity

Expected release artifact filename: `Enkryon-v1.3.0.apk`.

The previous APK and checksum are superseded. No checksum is approved until the balance-neutrality candidate completes the full Android release gate.

## Android compatibility

- Package: `com.intian.enkryon`
- Version name: `1.3.0`
- Version code: `102410300`
- Minimum Android API: `24`
- Target Android API: `36`
- Architectures: `arm64-v8a`, `armeabi-v7a`

## Release gate

A new complete Windows test/coverage gate, compilation check, whitespace check,
signed Android build, clean install, official v1.2.0 in-place upgrade,
Pass-through balance-neutrality check, backup/restore check, and relaunch check
are required before approval.

No APK checksum is approved while this correction is in progress.
