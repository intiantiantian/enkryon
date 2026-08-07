# Enkryon v1.3.0

Release date: `2026-08-07`

Release status: `RELEASE CANDIDATE`

## Summary

Enkryon 1.3 adds Pass-through Transfers for completed cash-out or
money-forwarding exchanges. One Pass-through record stores two linked effects
on user-owned accounts: the source account is the outflow and the destination
account is the inflow. The principal never becomes Income, Expense, category
activity, or posted net cash flow.

## User-visible changes

- Added explicit Internal and Pass-through modes to Transfer Funds.
- Added optional counterparty metadata for Pass-through exchanges.
- Added visible PASS-THROUGH activity treatment on Dashboard and Activity
  History.
- Added searchable counterparty and transfer-kind text.
- Added Advanced Internal and Pass-through filters while the primary Transfer
  filter continues to show both kinds.
- Pass-through activity uses explicit linked wording such as
  `Cash outflow | Bank inflow` so it is not confused with moving the same
  physical money between the user's own accounts.
- Added backup format 4 so transfer kind and counterparty survive export,
  replacement restore, and relaunch.

## Financial behavior

For a Pass-through principal, the source account decreases by the exact amount
and the destination account increases by the same exact amount. The combined
all-account balance does not change. Income, Expenses, category totals, and
posted net cash flow do not change. All amounts remain integer centavos.

A real service fee is recorded separately as a normal posted Expense. Pass-through
principal is never silently reduced by a fee.

## Upgrade and stored data

- Upgrade source: official `v1.2.0`
- In-place upgrade result: `PENDING`
- Database migration result: desktop migration tests `PASSED`; Android upgrade
  verification `PENDING`
- User-data preservation result: `PENDING`
- Post-upgrade force-stop and relaunch result: `PENDING`

Migration 7 extends `account_transfers` with constrained `internal` and
`pass_through` kinds plus optional counterparty metadata. Every transfer that
exists before migration 7 becomes Internal. Migrations 1 through 6 remain
unchanged.

New exports use backup format 4. Compatible formats 1 through 3 remain
restorable; older transfers normalize to Internal with no counterparty, while
existing Pending/posting compatibility rules remain unchanged.

## Android compatibility

- Package: `com.intian.enkryon`
- Version name: `1.3.0`
- Version code: `PENDING FINAL BUILD`
- Minimum Android API: `24`
- Target Android API: `36`
- Architectures: `arm64-v8a`, `armeabi-v7a`
- Physical-device verification: `PENDING`

## Known limitations

- Financial data remains local to the device unless the user exports a backup.
- Restore replaces current data; it does not merge backup and current records.
- Pass-through v1.3.0 models one completed equal-principal exchange. Partial
  settlement, multiple counterparties, loans, debts, receivables, and multi-leg
  exchanges remain outside this release.
- Pending Transactions remain a separate non-posting income/expense state.

## Verification

- Task 6 focused backup/recovery tests: `103 passed`
- Automated tests before release-candidate closeout: `820 passed in 22.63s`
- Total branch coverage: `84%`
- Python compilation: `PASSED`
- Git whitespace check: `PASSED`
- Controlled format-4 export/Clear All Data/restore/relaunch: `PASSED`
- GitHub Actions: `PENDING`
- APK signature: `PENDING`
- APK alignment: `PENDING`
- APK checksum verification: `PENDING`
- Clean install and launch: `PENDING`
- Official v1.2.0-to-v1.3.0 in-place upgrade: `PENDING`
- Final Android Pass-through workflow: `PENDING`
- Final backup format 4 recovery: `PENDING`

## Artifact

- Filename: `Enkryon-v1.3.0.apk`
- Size: `PENDING FINAL BUILD`
- SHA-256: `PENDING FINAL BUILD`
- Signing certificate SHA-256:
  `E3:D2:9B:10:8A:69:4A:ED:75:87:FD:99:5F:00:B0:22:64:97:B5:66:A6:53:3A:E8:47:EF:23:71:A0:12:C4:3D`
