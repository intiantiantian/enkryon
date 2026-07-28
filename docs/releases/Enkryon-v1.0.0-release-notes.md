# Enkryon v1.0.0

Release date: `2026-07-28`

## Summary

Enkryon 1.0 is the first stable release of the offline-first personal
finance tracker. It combines exact centavo calculations, safe database
migrations, user-controlled backup and restore, advanced transaction
filters, and a responsive mobile interface with completed beta and
accessibility verification.

## User-visible changes

- Added combined transaction search and filters for account, transaction
  type, category group, category, and inclusive date range.
- Added versioned JSON backup export, validated replacement restore, and a
  backup-before-clear recovery path.
- Changed Transaction History to virtualized rendering for responsive
  10,000-record histories.
- Improved narrow-screen, enlarged-font, keyboard, Back-button, and
  destructive-confirmation behavior across all six screens.
- Fixed large-history memory exhaustion and unstable recycled-card spacing.

## Upgrade and stored data

- Upgrade tested from: `v0.8.0`
- In-place upgrade result: `PENDING FINAL RELEASE-CANDIDATE VERIFICATION`
- Database migration result: `NOT APPLICABLE` for `v0.8.0` to `v1.0.0`;
  both use database migration version 4.
- User-data preservation result: `PENDING FINAL RELEASE-CANDIDATE VERIFICATION`

Legacy `v0.3.0` and `v0.7.0` database fixtures already passed migration
verification without changes to IDs, relationships, notes, dates, exact
centavo values, or totals. Enkryon backups remain user-controlled JSON
documents; restore replaces current data after validation and explicit
confirmation.

## Android compatibility

- Package: `com.intian.enkryon`
- Minimum Android API: `24`
- Target Android API: `36`
- Architectures: `arm64-v8a`, `armeabi-v7a`

## Known limitations

- Financial data remains local to the device unless the user exports a
  backup.
- Restore replaces current data; it does not merge backup and current
  records.
- Cloud synchronization, budgets, reports, and recurring transactions are
  outside the version 1.0 scope.

## Verification

- Automated tests: `504 PASSED BEFORE VERSION 1.0 CLOSEOUT CHANGES`
- GitHub Actions: `PENDING RELEASE COMMIT`
- Signature: `PENDING FINAL RELEASE-CANDIDATE VERIFICATION`
- Alignment: `PENDING FINAL RELEASE-CANDIDATE VERIFICATION`
- Clean install and launch: `PENDING FINAL RELEASE-CANDIDATE VERIFICATION`
- Official in-place upgrade: `PENDING FINAL RELEASE-CANDIDATE VERIFICATION`
- Core workflow smoke test: `PENDING FINAL RELEASE-CANDIDATE VERIFICATION`

## Artifact

- Filename: `Enkryon-v1.0.0.apk`
- Size: `PENDING FINAL BUILD`
- SHA-256: `PENDING FINAL BUILD`
- Signing certificate SHA-256:
  `E3:D2:9B:10:8A:69:4A:ED:75:87:FD:99:5F:00:B0:22:64:97:B5:66:A6:53:3A:E8:47:EF:23:71:A0:12:C4:3D`
