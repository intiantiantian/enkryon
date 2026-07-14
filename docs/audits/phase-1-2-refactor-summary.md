# Phase 1.2 Refactor Summary

## Status

Phase 1.2 focused on architecture cleanup, database safety, and regression testing before starting the design system phase.

## Completed Work

### Branching

- Created a dedicated refactor branch.
- Used small atomic commits.
- Verified changes incrementally after each refactor step.

### Naming Cleanup

- Standardized project naming from `Enkyron` to `Enkryon`.
- Updated app class naming.
- Updated README references.

### Database Safety

- Enabled SQLite foreign key enforcement.
- Added a database path helper.
- Moved runtime database usage toward the app user data directory.
- Ensured the database directory is created automatically.
- Removed `.db` files from APK packaging.
- Added `.db` files to Git ignore rules.
- Documented database storage behavior.

### Android Verification

- Built a debug APK.
- Installed and tested on Android.
- Confirmed basic navigation and data persistence.
- Documented Android smoke test results.

### Architecture Documentation

- Added architecture boundary documentation.
- Defined responsibilities for:
  - `main.py`
  - `screens/`
  - `services/`
  - `database/`
  - `widgets/`
  - `utils/`
  - `theme/`

### Service Layer Cleanup

- Inspected unused imports and unused variables.
- Confirmed raw SQLite access is contained inside `database/`.
- Removed snackbar behavior from transaction services.
- Removed dialog-dismiss behavior from transaction services.
- Removed direct widget creation from transaction services.
- Changed transaction services to return data instead of rendering UI.

### Add Transaction Cleanup

Extracted helper logic from `screens/add_transaction.py`:

- Amount keypad behavior → `utils/amount_input.py`
- Transaction validation → `utils/transaction_validation.py`
- Date/time formatting → `utils/transaction_datetime.py`
- Transaction payload creation → `utils/transaction_payload.py`

### Test Coverage Added

Added utility tests for:

- Amount input behavior
- Transaction validation
- Transaction payload creation

Added repository tests for:

- Accounts
- Category groups
- Categories
- Transactions
- Totals
- Current balance
- Transaction filtering
- Referenced account delete protection
- Referenced category delete protection

## Current Test Status

All tests pass.

## Known Remaining Issues

These are intentionally left for future phases:

- `screens/add_transaction.py` is still large.
- Money is still stored as `REAL`.
- Account duplicate validation is not yet case-insensitive.
- No migration system exists yet.
- UI still has hardcoded colors.
- Design tokens are not yet implemented.
- Reusable design-system components are not yet implemented.

## Phase 1.2 Result

Phase 1.2 significantly improved Enkryon's maintainability and safety.

The app now has:

- Safer database handling.
- Cleaner service boundaries.
- Better separation between services, screens, widgets, and utils.
- Basic automated regression tests.
- Documented architecture rules.
- Android smoke test evidence.

## Recommended Next Phase

Proceed to Phase 1.3: Design System.

Recommended first Phase 1.3 steps:

1. Define Enkryon brand identity.
2. Document emerald/gold color usage.
3. Create centralized design tokens.
4. Replace hardcoded colors gradually.
5. Create reusable UI components.