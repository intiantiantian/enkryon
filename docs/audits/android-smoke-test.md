# Android Smoke Test

## Context

This smoke test was performed after the database safety refactor.

Recent database-related changes:

- SQLite foreign keys are now enforced.
- Local `.db` files are excluded from APK packaging.
- A database path helper was added.
- The app now uses the database path helper for SQLite connections.
- Database storage behavior is documented.

## Environment

- App: Enkryon
- Build type: Debug APK
- Test device: Android device
- Tested date: July 15, 2026

## Smoke Test Checklist

- [x] APK builds successfully.
- [x] APK installs successfully.
- [x] App opens without crashing.
- [x] Dashboard loads.
- [x] Accounts screen opens.
- [x] Categories screen opens.
- [x] Add Transaction screen opens.
- [x] Transaction history screen opens.
- [x] Account can be created.
- [x] Category group can be created.
- [x] Category can be created.
- [x] Income transaction can be added.
- [x] Expense transaction can be added.
- [x] App can be closed and reopened.
- [x] Data persists after reopening the app.

## Result

Passed.

## Notes

This was a smoke test only. It confirms that the APK can build, install, open, navigate, create basic data, and persist data after reopening.

This does not replace a full regression test.