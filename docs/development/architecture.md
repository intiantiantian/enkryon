# Enkryon Architecture Boundaries

This document defines where code should belong as Enkryon grows.

The goal is to keep the app easier to maintain by preventing screens, services, database files, and widgets from overlapping too much.

## Folder Responsibilities

### `main.py`

Responsible for:

* Starting the KivyMD app.
* Loading KV files.
* Creating the screen manager.
* Registering screens.
* Applying app-level theme settings.

Should avoid:

* Business logic.
* SQL queries.
* Transaction calculations.
* Screen-specific behavior.

---

### `screens/`

Screens are responsible for UI coordination.

They may:

* Read values from widgets.
* Respond to button presses.
* Open menus and dialogs.
* Call services or repositories.
* Navigate between screens.
* Show snackbars or error messages.
* Render widgets into layouts.

They should avoid:

* Raw SQL queries.
* Complex business rules.
* Reusable formatting logic.
* Creating database connections directly when a repository/service can do it.
* Large repeated UI structures that should become widgets.

Example:

```text
Good:
Screen gets input → calls service/repository → updates UI

Avoid:
Screen gets input → builds SQL query → calculates totals → creates repeated widgets manually
```

---

### `services/`

Services are responsible for business workflows.

They may:

* Validate app-level rules.
* Coordinate multiple repositories.
* Prepare data for screens.
* Return success/failure results.
* Handle transaction/account/category workflows.

They should avoid:

* Creating Kivy widgets.
* Adding widgets directly to layouts.
* Showing snackbars.
* Navigating between screens.
* Depending on screen IDs.

A service should return data or a result. The screen should decide how to display it.

Example:

```text
Good:
service returns transactions

Avoid:
service creates TransactionCard widgets and inserts them into the screen
```

---

### `database/`

Database files are responsible for persistence.

They may:

* Connect to SQLite.
* Create tables.
* Run SQL queries.
* Insert, update, delete, and fetch records.
* Enforce database-level constraints.

They should avoid:

* Kivy widgets.
* Snackbar messages.
* Screen navigation.
* App layout decisions.
* Visual formatting.

Repositories should stay focused on data access.

---

### `widgets/`

Widgets are responsible for reusable UI pieces.

They may:

* Define reusable cards.
* Define reusable buttons.
* Define empty states.
* Define repeated UI components.
* Accept data and display it.

They should avoid:

* Raw SQL queries.
* Owning business workflows.
* Creating or deleting records directly.
* Performing app-wide navigation unless specifically designed for it.

Example widgets:

* TransactionCard
* EmptyState
* SummaryCard
* AppTopBar
* ConfirmDialogContent

---

### `utils/`

Utils are responsible for small reusable helper functions.

They may:

* Format currency.
* Format dates.
* Normalize strings.
* Convert values.
* Provide small validation helpers.

They should avoid:

* Database writes.
* Kivy screen logic.
* Complex workflows.
* App state.

---

### `theme/`

Theme files are responsible for design constants.

They may define:

* Semantic colors.
* Typography sizes.
* Spacing.
* Radius values.
* Component dimensions.
* Elevation values.

They should avoid:

* Screen behavior.
* Business logic.
* SQL queries.
* Data formatting unrelated to visual design.

---

## Refactoring Rule

When changing code, ask:

```text
Is this UI coordination?
→ Put it in screens/

Is this business workflow?
→ Put it in services/

Is this SQL or persistence?
→ Put it in database/

Is this reusable UI?
→ Put it in widgets/

Is this a small generic helper?
→ Put it in utils/

Is this a visual design constant?
→ Put it in theme/
```

## Current Refactor Direction

Phase 5 completed the current architecture separation:

1. Repository queries return named records rather than positional tuples.
2. Managed connections centralize foreign-key setup, rollback, and cleanup.
3. Transaction form state owns dependent account, type, group, category,
   date, time, notes, and edit-state transitions.
4. Transaction, account, and category services own workflow validation and
   translate repository outcomes into explicit results.
5. Screens coordinate input, navigation, dialogs, messages, and rendering.
6. Shared transaction-list actions own repeated filtering, editing,
   deletion, confirmation-dialog, and refresh behavior.
7. Shared action-result rendering owns snackbar and refresh sequencing.

Phase 6 changed layouts and interaction patterns while preserving these
boundaries.

Phase 7 added recovery-specific service boundaries:

1. `services/backup_exporter.py` creates versioned backup documents without
   involving interface code.
2. `services/backup_validator.py` validates the complete document and prepares
   preview metadata before current data can change.
3. `services/backup_restorer.py` owns the confirmed replacement transaction,
   dependency ordering, ID preservation, sequence restoration, integrity
   checks, and rollback behavior.
4. `services/document_transfer.py` isolates desktop file access and Android
   document-picker behavior from Settings.
5. `screens/settings.py` coordinates previews, confirmations, user feedback,
   and navigation without owning backup-format or persistence rules.

Phase 8 preserved these boundaries while adding transaction discovery:

1. `screens/transaction_filter_state.py` owns filter selections and their
   dependent transitions.
2. `database/transaction_repository.py` owns search, combined query
   construction, stable newest-first ordering, and indexed data access.
3. Shared screen actions coordinate filtering, editing, deletion, and
   refresh behavior without duplicating those workflows.
4. `widgets/transaction_list.py` adapts repository records into lightweight
   `RecycleView` data, while recycled cards remain display-only widgets.

Phase 9 verified the same boundaries with 10,000 transactions. Virtualization
keeps the full history responsive without moving SQL, filtering rules, or
record mutations into reusable cards.

Update 1 extends the same boundaries for account transfers:

1. `database/transfer_repository.py` owns the atomic transfer record,
   constraints, CRUD operations, and account-direction queries.
2. `database/activity_repository.py` combines transactions and transfers in
   SQL before stable newest-first ordering and limiting.
3. `services/transfer_services.py` owns create, edit, delete, restore, and
   validation workflows; `services/activity_services.py` prepares the unified
   feed for screens.
4. `screens/transfer_form_state.py` owns UI-independent source, destination,
   amount, date/time, notes, and edit state.
5. `screens/transfer.py` coordinates the form and navigation without owning
   SQL or financial calculations.
6. Shared transaction-list actions and widgets dispatch by activity record
   type while remaining presentation and coordination code.
7. Backup export, validation, and restore preserve transfers as first-class
   records without weakening the version-1 compatibility path.

Update 2 extends the architecture without introducing a separate Pending
transaction repository:

1. `database/transaction_repository.py` owns status-aware CRUD, posted-only
   totals, and the compare-and-set transition from `temporary` to `posted`.
2. `database/activity_repository.py` combines transfers, posted transactions,
   and Pending transactions while enforcing posted-only Income/Expense views.
3. `services/transaction_services.py` owns Pending save, edit, post, delete, and
   restore results without importing Kivy.
4. `screens/transaction_form_state.py` and
   `screens/transaction_form_actions.py` own UI-independent status and action
   presentation state.
5. Transaction screens coordinate confirmation, navigation, refresh, and user
   feedback; reusable cards display status and dispatch actions but do not own
   posting rules.
6. Backup format, validation, and restore preserve status in format 3 while
   normalizing older formats before replacement recovery.

Update 3 extends the existing transfer path rather than adding a second ledger:

1. Migration 7 adds constrained `internal` and `pass_through` kinds plus optional
   counterparty metadata to `account_transfers`.
2. `database/transfer_repository.py` and `services/transfer_services.py` keep
   create, edit, delete, restore, exact-centavo validation, and failure handling
   shared between both kinds.
3. `screens/transfer_form_state.py` preserves transfer kind and counterparty
   independently of Kivy, while `screens/transfer.py` owns the visible mode and
   linked outflow/inflow explanation.
4. `database/activity_repository.py` carries kind and counterparty through the
   unified history so Transfer includes both kinds and Advanced Filters can
   distinguish them without affecting Income, Expense, or Pending semantics.
5. Shared activity cards present Pass-through as linked account effects, for
   example `Cash outflow | Bank inflow`, instead of implying an Internal
   Transfer of the same physical money.
6. Backup format 4 preserves kind and counterparty; formats 1 through 3 normalize
   older transfers to Internal during validated replacement restore.

Update 4 keeps estimated interest outside the posted transaction ledger until
reconciliation:

1. `database/interest_repository.py` owns effective-dated profile persistence,
   idempotent accrual rows, bounded history access, reconciliation links, and
   interest-only removal.
2. `services/interest_services.py` owns Actual/365 calculation, exact
   sub-centavo carry, posted closing-balance selection, missed-day generation,
   reconciliation, and removal results without importing Kivy.
3. `screens/account_interest_state.py` owns UI-independent APR/effective-date
   parsing and account interest presentation state.
4. `screens/accounts.py` coordinates the settings, reconciliation, Disable, and
   Remove Interest overlays without owning SQL or interest arithmetic.
5. `widgets/interest_dialog.py` and `kv/interest_dialog.kv` remain presentation
   components; estimates are visibly non-posting and actual credits require an
   explicit reconciliation action.
6. Reconciled credits deliberately reuse the normal posted Income transaction
   path, so balances, Income totals, Activity History, and later statistics have
   one canonical financial record.
7. Backup format 5 preserves interest profiles/accruals while formats 1 through
   4 restore with empty interest tables and keep all older financial semantics.

## Rule for Future Commits

Each refactor commit should be small and reversible.

Good examples:

```text
docs: document architecture boundaries
refactor: remove unused imports from transaction screen
refactor: separate transaction card rendering from service
refactor: consolidate snackbar helper usage
```

Avoid vague commits:

```text
update
fix
changes
refactor everything
```
