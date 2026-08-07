# Enkryon v1.3.0

Release date: `2026-08-07`

Release status: `ACCOUNTING CORRECTION CANDIDATE`

## Accounting correction notice

Publication was stopped before merge/tag. The previous candidate derived
Pass-through balance effects from the parent without explicit external movement
records. That APK evidence is superseded. The corrected candidate persists one
explicit outflow and one explicit inflow and must repeat the Android release
gate before approval.

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

The Pass-through parent has zero direct balance effect. A complete explicit
outflow/inflow pair changes the participating accounts by equal and opposite
exact amounts. An incomplete or inconsistent pair contributes zero. The combined
all-account balance, Income, Expenses, category totals, and posted net cash flow
remain unchanged. All amounts remain integer centavos.

A real service fee is recorded separately as a normal posted Expense. Pass-through
principal is never silently reduced by a fee.

## Upgrade and stored data

- Upgrade source: official `v1.2.0`
- In-place upgrade result: `PASSED`
- Database migration result: `PASSED` on desktop and Android
- User-data preservation result: `PASSED`
- Post-upgrade force-stop and relaunch result: `PASSED`

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
- Version code: `102410300`
- Minimum Android API: `24`
- Target Android API: `36`
- Architectures: `arm64-v8a`, `armeabi-v7a`
- Physical-device verification: `PASSED`

## Known limitations

- Financial data remains local to the device unless the user exports a backup.
- Restore replaces current data; it does not merge backup and current records.
- Pass-through v1.3.0 models one completed equal-principal exchange. Partial
  settlement, multiple counterparties, loans, debts, receivables, and multi-leg
  exchanges remain outside this release.
- Pending Transactions remain a separate non-posting income/expense state.

## Verification

- Task 6 focused backup/recovery tests: `103 passed`
- Final automated tests: `824 passed in 22.65s`
- Total branch coverage: `84%`
- Python compilation: `PASSED`
- Git whitespace check: `PASSED`
- GitHub Actions on the release branch: `PASSED`
- WSL release build: `PASSED`
- APK package/version identity: `PASSED`
- APK signature: `PASSED`
- APK alignment: `PASSED`
- APK checksum verification: `PASSED`
- Clean install and launch: `PASSED`
- Official v1.2.0-to-v1.3.0 in-place upgrade: `PASSED`
- Existing v1.2.0 transfers remained Internal after migration 7: `PASSED`
- Posted and Pending transaction status preservation: `PASSED`
- Final Android Pass-through workflow: `PASSED`
- Force-stop and relaunch persistence: `PASSED`
- Backup format 4 export/Clear All Data/restore/relaunch: `PASSED`

## Artifact

- Filename: `Enkryon-v1.3.0.apk`
- Size: `45,775,760 bytes`
- SHA-256:
  `fcb2766b02be8d344e534ae0961f2aedf0e3dbb509c3ce4106f90a19d484289c`
- Signing certificate SHA-256:
  `E3:D2:9B:10:8A:69:4A:ED:75:87:FD:99:5F:00:B0:22:64:97:B5:66:A6:53:3A:E8:47:EF:23:71:A0:12:C4:3D`
