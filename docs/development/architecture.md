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

Phase 6 may change layouts and interaction patterns, but it should preserve
these boundaries and keep persistence and financial rules out of screens.

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
