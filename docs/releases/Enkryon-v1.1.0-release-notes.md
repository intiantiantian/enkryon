# Enkryon v1.1.0

Release date: `2026-08-04` (candidate; publication pending)

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

- Upgrade tested from: `v1.0.0`
- In-place upgrade result: `PENDING FINAL ANDROID VERIFICATION`
- Database migration result: `AUTOMATED TESTS PASS; ANDROID VERIFICATION PENDING`
- User-data preservation result: `PENDING FINAL ANDROID VERIFICATION`

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

## Verification

- Focused implementation checkpoints: `PASS`
- Complete automated tests: `PENDING FINAL RELEASE GATE`
- GitHub Actions: `PENDING RELEASE CANDIDATE PUSH`
- Signature: `PENDING FINAL RELEASE BUILD`
- Alignment: `PENDING FINAL RELEASE BUILD`
- Clean install and launch: `PENDING FINAL ANDROID VERIFICATION`
- Official in-place upgrade: `PENDING FINAL ANDROID VERIFICATION`
- Core workflow smoke test: `PENDING FINAL ANDROID VERIFICATION`

## Artifact

- Filename: `Enkryon-v1.1.0.apk`
- Size: `PENDING FINAL BUILD`
- SHA-256: `PENDING FINAL BUILD`
- Signing certificate SHA-256:
  `E3:D2:9B:10:8A:69:4A:ED:75:87:FD:99:5F:00:B0:22:64:97:B5:66:A6:53:3A:E8:47:EF:23:71:A0:12:C4:3D`
