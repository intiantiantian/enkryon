# Enkryon v1.3.0

Release date: `2026-08-08`

Release status: `RELEASED`

## Summary

Enkryon 1.3 adds Pass-through Transfers for completed cash-out or
money-forwarding exchanges. A Pass-through stores the participating accounts,
exact principal, date/time, notes, and optional counterparty for history,
search, filtering, backup, and recovery.

The final accounting rule is strict: a Pass-through represents the complete
counterparty exchange and has zero balance effect on each participating
account. It is neither Income nor Expense.

## User-visible changes

- Added explicit Internal and Pass-through modes to Transfer Funds.
- Added optional counterparty metadata for Pass-through exchanges.
- Pass-through account roles use `PAID FROM` and `RECEIVED INTO`.
- Pass-through guidance states that the complete exchange leaves both account
  balances unchanged.
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

- Upgrade source verified: official `v1.2.0`.
- Migration 7 adds Internal/Pass-through kind and optional counterparty.
- Migration 8 remains superseded development history.
- Migration 9 removes the temporary Pass-through movement table, triggers, and
  index and locks the balance-neutral model.
- Every transfer that exists before migration 7 becomes Internal.
- Backup format 4 preserves transfer kind and counterparty.
- Compatible formats 1 through 3 remain restorable; older transfers normalize
  to Internal.

## Verification

- Final Windows gate: `830 passed in 23.65s`.
- Total branch coverage: `84%`.
- Main-branch sanity gate: `830 passed in 23.32s`.
- Python compilation: `PASSED`.
- Git whitespace check: `PASSED`.
- Desktop Pass-through balance-neutrality check: `PASSED`.
- Signed Android clean install and launch: `PASSED`.
- Official v1.2.0-to-v1.3.0 in-place upgrade: `PASSED`.
- Android Pass-through balance-neutrality workflow: `PASSED`.
- Backup format 4 export, Clear All Data, restore, and relaunch: `PASSED`.
- Main merge commit: `1a0867c45ab7922c0d304cbc47331e485319e2b6`.

## Android compatibility

- Package: `com.intian.enkryon`
- Version name: `1.3.0`
- Version code: `102410300`
- Minimum Android API: `24`
- Target Android API: `36`
- Architectures: `arm64-v8a`, `armeabi-v7a`

## Artifact

- Filename: `Enkryon-v1.3.0.apk`
- Size: `45,776,720 bytes`
- SHA-256: `EBEBFD56F1FFE55785E5C289D945F4C85BB8375FB81F0CF7A185142B904FBE78`
- Signing certificate SHA-256:
  `E3:D2:9B:10:8A:69:4A:ED:75:87:FD:99:5F:00:B0:22:64:97:B5:66:A6:53:3A:E8:47:EF:23:71:A0:12:C4:3D`

## Known limitations

- Financial data remains local to the device unless the user exports a backup.
- Restore replaces current data; it does not merge backup and current records.
- Pass-through v1.3.0 models one completed equal-principal exchange. Partial
  settlement, multiple counterparties, loans, debts, receivables, and unequal
  multi-leg exchanges remain outside this release.
- Pending Transactions remain a separate non-posting income/expense state.
