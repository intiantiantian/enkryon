# Enkryon v1.2.0

Release date: `2026-08-05`

Release status: `RELEASE CANDIDATE — PENDING FINAL ANDROID VERIFICATION`

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
- Added pending-specific confirmation, deletion, undo, empty-state, search, and
  responsive-layout behavior.
- Added backup format 3 so posted and Pending status survives export, Clear All
  Data, replacement restore, and relaunch.

## Upgrade and stored data

- Upgrade tested from: `v1.1.0 — PENDING FINAL DEVICE TEST`
- In-place upgrade result: `PENDING FINAL ANDROID VERIFICATION`
- Database migration result: `AUTOMATED TESTS PASS; DEVICE UPGRADE PENDING`
- User-data preservation result: `PENDING FINAL ANDROID VERIFICATION`

Migration 6 extends existing transactions with a constrained posting status.
Every transaction already stored by v1.1.0 becomes posted, so upgrading cannot
silently remove an existing transaction from balances or totals. New Pending
records use the same transaction identity and become financially effective only
through one atomic status transition.

New exports use backup format 3 and require exact `posted` or `temporary` status
on every transaction. Compatible format-1 and format-2 documents remain
restorable; their transactions normalize to posted because those formats
predate Pending status. Restore remains replacement-only and never merges
datasets.

## Android compatibility

- Package: `com.intian.enkryon`
- Minimum Android API: `24`
- Target Android API: `36`
- Architectures: `arm64-v8a`, `armeabi-v7a`

## Known limitations

- Financial data remains local to the device unless the user exports a backup.
- Restore replaces current data; it does not merge backup and current records.
- Pending records do not auto-post, auto-expire, or trigger reminders.
- Pass-through cash-out activity is not part of this release; it is planned as
  a separate transfer capability because it changes account balances without
  becoming Income or Expenses.
- The earlier official v1.0.0-to-v1.1.0 physical-device upgrade was waived.
  Users should export a backup before upgrading until the v1.1.0-to-v1.2.0
  release test is complete.

## Verification

- Automated tests: `PENDING FINAL RELEASE GATE`
- GitHub Actions: `PENDING`
- Signature: `PENDING`
- Alignment: `PENDING`
- Clean install and launch: `PENDING`
- Official in-place upgrade: `PENDING`
- Core workflow smoke test: `PENDING`

## Artifact

- Filename: `Enkryon-v1.2.0.apk`
- Size: `PENDING FINAL RELEASE BUILD`
- SHA-256: `PENDING FINAL RELEASE BUILD`
- Signing certificate SHA-256:
  `E3:D2:9B:10:8A:69:4A:ED:75:87:FD:99:5F:00:B0:22:64:97:B5:66:A6:53:3A:E8:47:EF:23:71:A0:12:C4:3D`
