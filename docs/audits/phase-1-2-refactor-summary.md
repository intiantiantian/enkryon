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

## Phase 1.2 Follow-up Status

The following observations were accurate when Phase 1.2 ended. This table
records what happened to them in later phases so historical notes are not
mistaken for current defects.

| Phase 1.2 observation | Current status |
|---|---|
| `screens/add_transaction.py` is still large. | Resolved in Phase 5 by extracting transaction form state, save/edit workflows, validation, payload creation, and shared action behavior; the remaining screen code coordinates keypad, menu, picker, and rendering interactions. |
| Money is stored as `REAL`. | Resolved in Phase 2; amounts now use integer centavos. |
| Account duplicate validation is not case-insensitive. | Resolved in Phase 2 through normalized application and database rules. |
| No migration system exists. | Resolved in Phase 2 with ordered, transactional migrations. |
| UI colors are hardcoded. | Design-system foundations were completed in Phase 1.3; remaining visual cleanup belongs to Phase 6. |
| Design tokens are not implemented. | Resolved in Phase 1.3. |
| Reusable design-system components are not implemented. | Initial components were completed in Phase 1.3; expansion continues in Phases 5 and 6. |

## Phase 1.2 Result

Phase 1.2 significantly improved Enkryon's maintainability and safety.

The app now has:

- Safer database handling.
- Cleaner service boundaries.
- Better separation between services, screens, widgets, and utils.
- Basic automated regression tests.
- Documented architecture rules.
- Android smoke test evidence.

## Historical Next Step

The next step recorded at the end of Phase 1.2 was Phase 1.3: Design
System. That phase and the later Phase 2 financial-correctness work have
since been completed. Current priorities are maintained in `ROADMAP.md`.
