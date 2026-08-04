# Enkryon v1.1.0

Release date: `2026-08-04`

## Summary

Enkryon 1.1 adds first-class account transfers. A transfer moves an exact
integer-centavo amount between two accounts without being counted as income or
expense, remains editable and auditable in Activity History, and is preserved
by the expanded backup and recovery flow.

## User-visible changes

- Added a dedicated Transfer Funds screen with source and destination account
  selectors, exact amount entry, date/time, and optional notes.
- Added transfer editing, confirmed deletion, and undo restoration.
- Added transfer cards, search, account/date/type filters, and direction-aware
  amounts to Dashboard and Activity History.
- Changed per-account balances to subtract outgoing transfers and add incoming
  transfers while keeping the all-accounts balance, Income, Expenses, and
  category totals unchanged.
- Changed the four Dashboard actions to a responsive two-by-two layout.
- Added account safety so an account used by a transfer cannot be deleted.
- Expanded backup, restore preview, Clear All Data, and rollback behavior to
  include transfers.

## Upgrade and stored data

- Upgrade tested from: `v1.0.0 baseline prepared; in-place upgrade test waived`
- In-place upgrade result: `NOT VERIFIED — TEST WAIVED BY RELEASE OWNER`
- Database migration result: `AUTOMATED TESTS PASS; PHYSICAL-DEVICE IN-PLACE UPGRADE NOT VERIFIED`
- User-data preservation result: `NOT VERIFIED FOR AN IN-PLACE UPGRADE`

Migration 5 creates one constrained `account_transfers` table and its
newest-first, outgoing, and incoming indexes. Existing migrations 1-4 remain
unchanged. A transfer is one atomic record rather than an unrelated expense
and income pair.

New exports use backup format 2 and include transfers. Compatible format-1
backups from Enkryon 1.0 remain restorable and are interpreted as containing
zero transfers. Restore still replaces current data after complete validation
and explicit confirmation; it does not merge datasets.

## Android compatibility

- Package: `com.intian.enkryon`
- Minimum Android API: `24`
- Target Android API: `36`
- Architectures: `arm64-v8a`, `armeabi-v7a`

## Known limitations

- Financial data remains local to the device unless the user exports a
  backup.
- Restore replaces current data; it does not merge backup and current records.
- A transfer may make the source account negative, matching Enkryon's existing
  ledger behavior for expenses.
- Transfers are intentionally excluded from Income, Expenses, and category
  totals. Statistical visualizations are planned for a later release.
- The official Android `v1.0.0` to `v1.1.0` in-place upgrade and
  post-upgrade backup/restore cycle were not executed for this release.
  Users should export a backup before upgrading.

## Verification

- Focused implementation checkpoints: `PASS`
- Complete automated tests: `637 PASSED; 83% TOTAL COVERAGE`
- GitHub Actions: `PASS`
- Signature: `PASS`
- Alignment: `PASS`
- Clean install and launch: `PASS`
- Official in-place upgrade: `SKIPPED BY RELEASE OWNER`
- Core workflow smoke test: `CLEAN-INSTALL CHECKS PASS; POST-UPGRADE CYCLE SKIPPED`

## Artifact

- Filename: `Enkryon-v1.1.0.apk`
- Size: `45,763,428 bytes`
- SHA-256: `3fa66d0e5804fd8bbb5b9707157f951dd062ef06d2f3f9377e4ed31c2c4db79a`
- Signing certificate SHA-256:
  `E3:D2:9B:10:8A:69:4A:ED:75:87:FD:99:5F:00:B0:22:64:97:B5:66:A6:53:3A:E8:47:EF:23:71:A0:12:C4:3D`
