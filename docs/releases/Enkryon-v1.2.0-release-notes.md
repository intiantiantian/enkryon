# Enkryon v1.2.0

Release date: `2026-08-06`

Release status: `RELEASE APPROVED`

## Summary

Enkryon 1.2 adds Pending Transactions. A pending income or expense remains
visible and searchable but does not affect account balances, Income, Expenses,
category totals, or other posted financial results until the user explicitly
posts it.

## User-visible changes

- Added Save as Pending and Post Transaction actions to the transaction form.
- Added visible PENDING status treatment and guarded post actions to Dashboard
  recent activity and Activity History.
- Added a Pending filter; Income and Expense filters now return posted records
  only.
- Added a collapsible Advanced Filters section in Activity History, with
  separate posted-type controls and Pending/Transfer controls.
- Added pending-specific confirmation, deletion, undo, empty-state, search, and
  responsive-layout behavior.
- Added backup format 3 so posted and Pending status survives export, Clear All
  Data, replacement restore, and relaunch.

## Upgrade and stored data

- Upgrade tested from: `v1.1.0`
- In-place upgrade result: `PASSED`
- Database migration result: `PASSED`
- User-data preservation result: `PASSED`
- Post-upgrade force-stop and relaunch result: `PASSED`

Migration 6 extends existing transactions with a constrained posting status.
Every transaction already stored by v1.1.0 becomes posted, so upgrading cannot
silently remove an existing transaction from balances or totals. New Pending
records use the same transaction identity and become financially effective only
through one atomic status transition.

The physical-device upgrade was performed with `adb install -r` over an
official v1.1.0 installation containing restored legacy data. Accounts,
categories, groups, transactions, transfers, notes, dates, balances, and exact
centavo values remained intact. Creating, posting, and relaunching a Pending
transaction after the upgrade passed without a duplicate financial effect.

New exports use backup format 3 and require exact `posted` or `temporary` status
on every transaction. Compatible format-1 and format-2 documents remain
restorable; their transactions normalize to posted because those formats
predate Pending status. Restore remains replacement-only and never merges
datasets.

A physical-device format-3 recovery cycle also passed: export, clean uninstall,
clean reinstall, replacement restore, Pending-state recovery, one-time posting,
force-stop, and relaunch all preserved the expected records and financial
semantics.

## Android compatibility

- Package: `com.intian.enkryon`
- Version name: `1.2.0`
- Version code: `102410200`
- Minimum Android API: `24`
- Target Android API: `36`
- Architectures: `arm64-v8a`, `armeabi-v7a`
- Physical-device verification: Xiaomi `2312DRA50G`, Android 16 / API 36

## Known limitations

- Financial data remains local to the device unless the user exports a backup.
- Restore replaces current data; it does not merge backup and current records.
- Pending records do not auto-post, auto-expire, or trigger reminders.
- Pass-through cash-out activity is not part of this release; it is planned as
  a separate transfer capability because it changes account balances without
  becoming Income or Expenses.
- The earlier official v1.0.0-to-v1.1.0 physical-device upgrade was waived.
  The official v1.1.0-to-v1.2.0 upgrade is verified, but users should still
  export a backup before every application upgrade.

## Verification

- Automated tests: `746 passed in 21.09s`
- Total branch coverage: `83%`
- Python compilation: `PASSED`
- Git whitespace check: `PASSED`
- GitHub Actions: `PASSED`
- WSL source synchronization: `PASSED`
- APK signature: `PASSED`
- APK alignment: `PASSED`
- APK checksum verification: `PASSED`
- Clean install and launch: `PASSED`
- Official in-place upgrade: `PASSED`
- Legacy-data preservation: `PASSED`
- Pending create/post/persistence checks: `PASSED`
- Backup format 3 export/restore/relaunch: `PASSED`
- Core workflow smoke test: `PASSED`

## Artifact

- Filename: `Enkryon-v1.2.0.apk`
- Size: `45,770,820 bytes`
- SHA-256:
  `b5e1942d160d19c78604c84099d203972f9f886dc66e49a1c66eaee3e2aebdc3`
- Signing certificate SHA-256:
  `E3:D2:9B:10:8A:69:4A:ED:75:87:FD:99:5F:00:B0:22:64:97:B5:66:A6:53:3A:E8:47:EF:23:71:A0:12:C4:3D`
