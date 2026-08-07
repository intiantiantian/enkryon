# Local Development and Testing

This document defines the supported local setup and the checks that must
pass before Enkryon changes are committed.

## Verified Environment

The Phase 3 baseline was verified with:

- Windows 10
- Python 3.13.14
- pytest 9.1.1
- pytest-cov 7.1.0

Other compatible Python 3.13 versions may work, but Python 3.13.14 is the
verified development and continuous-integration version.

## Dependency Files

- `requirements.txt` contains application runtime dependencies.
- `requirements-dev.txt` installs runtime dependencies and pinned
  development-only testing tools.
- `buildozer.spec` separately defines dependencies packaged in the Android
  application.

Development tools must not be added to the Android Buildozer requirements.

## Create a Development Environment

From the project root in Windows Command Prompt:

```bat
py -3.13 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

When returning to the project later, activate the existing environment:

```bat
.venv\Scripts\activate
```

## Required Local Checks

Run the complete test suite with branch coverage:

```bat
python -m pytest -q --cov --cov-report=term-missing
```

Compile the Python source files to detect syntax problems:

```bat
python -m compileall -q main.py database screens services theme utils widgets tests
```

Check Git changes for whitespace errors:

```bat
git diff --check
```

Inspect the working tree:

```bat
git status --short
```

## Coverage Baseline

The initial Phase 3 application-wide baseline is `51%` branch coverage.

The strongest coverage is concentrated in the highest-risk core areas:

- Database migrations
- Transaction repositories and totals
- Exact money conversion and formatting
- Transaction validation and payload creation
- Transaction services

Screen and interactive-widget coverage remains lower because importing a
Kivy interface is not the same as exercising its behavior. The current
headless smoke test verifies that the application entry point and all six
screen modules can import successfully.

The baseline is informational. Phase 3 does not impose an arbitrary
percentage gate; new tests should target meaningful financial, migration,
service, and failure behavior.

## Phase 6 Interface Regression

Phase 6 began with `252` tests. Its implementation regression contained
`391` passing tests, and the documentation closeout adds four tests for a
final total of `395` passing tests.

Automated coverage now includes source-level responsive-layout contracts,
transaction-form preservation, actionable empty states, shared overlay
behavior, option selection, floating-label boundaries, Dashboard amount
capacity, and overlay-first Back handling.

Real rendering still requires application checks. Relevant Phase 6
checkpoints used these conditions:

- Small `S / 90%` profile.
- One medium or desktop profile.
- Default and enlarged system font.
- Empty, populated, validation-error, destructive, and long-content states.
- Android checks for keyboard, safe-area, and Back behavior.
- Desktop Escape behavior for active overlays.

The two final regression corrections received focused automated and
real-application checks. The complete all-profile manual checklist was not
repeated afterward; that explicit evidence limit is recorded in
`docs/audits/phase-6-verification.md`.

Future interface changes must run their focused tests, the complete suite,
and the device or desktop checks relevant to the changed behavior.

### Update 2 Task 5 activity and financial integration gate

Task 5 adds posting status to the shared Dashboard and Activity History filter
contract. Run this focused gate before the complete suite:

```bat
python -m pytest -q ^
tests/test_activity_repository.py ^
tests/test_activity_services.py ^
tests/test_transaction_filter_state.py ^
tests/test_transaction_list_actions.py ^
tests/test_transaction_screen_workflows.py ^
tests/test_pending_activity_integration.py ^
tests/test_transaction_history_performance.py ^
tests/test_responsive_layout.py ^
tests/test_accessibility_semantics.py ^
tests/test_update2_contract.py
```

The gate verifies explicit Pending controls on Dashboard and Activity History,
posted-only Income and Expense views, Pending-only transaction results, shared
filter-state forwarding, account/group/category/search/date combinations,
status-specific empty states, exact balance and total exclusion, one-time
posting movement between views, responsive five-control layouts, non-color-only
labels, and status-index use for 10,000 mixed records.

The complete Task 5 gate is expected to report `725 passed` with approximately
`83%` total branch coverage. Because the checkpoint changes visible filters,
also perform these real-application checks before committing:

1. Create one posted income, one posted expense, one pending income, one pending
   expense, and one transfer with recognizable notes.
2. Confirm `All` shows all five newest-first.
3. Confirm `INCOME` and `EXPENSE` show only their posted records.
4. Confirm `PENDING` shows both pending records and no transfer.
5. Combine Pending with account, search, category, and date filters.
6. Post one pending record and confirm it leaves Pending, enters the matching
   posted type, and changes the exact balance and total once.
7. Check both filter rows on a narrow window and enlarged system text.

### Update 2 Task 6 backup and recovery gate

Task 6 advances exports to backup format 3 while preserving strict validation
and replacement-only restore. Run this focused gate before the complete suite:

```bat
python -m pytest -q ^
tests/test_backup_format.py ^
tests/test_backup_exporter.py ^
tests/test_backup_validator.py ^
tests/test_backup_restorer.py ^
tests/test_pending_backup_recovery.py ^
tests/test_recovery_contract.py ^
tests/test_document_transfer.py ^
tests/test_settings_screen_workflows.py ^
tests/test_update2_contract.py
```

The gate verifies exact format-3 status export, posted/Pending round trips,
format-1 empty-transfer normalization, format-2 transfer preservation, default
posted status for both older formats, malformed-status rejection before
replacement, record counts, IDs, sequences, foreign keys, integrity, Clear All
Data, rollback, restore preview, document transfer, and Settings workflows.

The complete Task 6 gate is expected to report `737 passed` with approximately
`83%` total branch coverage. Also perform one real-application recovery check:

1. Create one posted transaction, one Pending transaction, and one transfer.
2. Record exact account balances, Income, and Expenses.
3. Export a backup and confirm the preview counts.
4. Clear All Data through the existing backup-first confirmation flow.
5. Restore the exported document and relaunch the app.
6. Confirm both transaction statuses, the transfer, record counts, and exact
   financial totals match the pre-export state.

## Phase 7 Recovery Regression

Phase 7 began with `395` tests. Its implementation closeout baseline contains
`446` passing tests with `79%` total branch coverage. Four Phase 7 closeout
tests bring the final expected total to `450` after documentation verification.

Automated recovery coverage includes:

- Versioned backup formatting and exact relational export.
- Complete validation before database modification.
- Restore previews and explicit replacement confirmation.
- Transactional restore, rollback, ID sequences, and foreign-key integrity.
- Empty, populated, malformed, incompatible, and corrupted backup cases.
- Desktop and Android document-transfer behavior.
- Settings backup, restore, cancellation, and backup-before-clear workflows.
- Kivy-thread dispatch for Android document-picker results.

The Android callback correction passed `10` focused document-transfer tests
and a broader `56`-test recovery and Settings regression. A rebuilt Android
debug APK then passed the previously failing restore-preview and
backup-before-clear checks. Replacement restore and Clear All Data were also
verified functionally on Android.

Restore in `v0.7.0` intentionally replaces current data. Backup merging is
deferred until after statistics, and cloud synchronization remains outside
Phase 7.

Future recovery changes must run focused exporter, validator, restorer,
document-transfer, and Settings tests; the complete suite; and the relevant
desktop or Android document-selection checks.

## Phase 8 Search and Filter Regression

Phase 8 began with `450` tests. Its implementation closeout baseline contains
`495` passing tests with `81%` total branch coverage. Four Phase 8 closeout
tests bring the final expected total to `499` after documentation verification.

Automated search and filter coverage includes:

- Search across notes, accounts, category groups, and categories.
- Literal wildcard handling and safe blank-note searches.
- Account, transaction-type, category-group, category, and inclusive
  date-range filters.
- Independent and combined filter behavior.
- Active-filter summaries, Reset All, and filter-specific no-results recovery.
- Shared Dashboard and Transaction History filter state and list actions.
- Stable newest-first ordering by date and transaction ID.
- Migration-managed transaction-history indexes.
- Backup compatibility across database versions 3 and 4.

The large-history regression seeds `10,000` transactions and verifies both
correct query results and SQLite query-plan use of the intended indexes. It
does not use a machine-dependent elapsed-time threshold.

Real-application checks confirmed successful migration and restart,
newest-first history, responsive account and category filtering, backup
export, and restore preview.

Future transaction-discovery changes must run focused filter-state,
repository, screen-workflow, migration, and backup tests; the complete suite;
and real-application checks relevant to the changed behavior.

## Phase 9 Release-Readiness Regression

Phase 9 began with `499` tests. Legacy-migration coverage raised the suite to
`500` tests, and the two large-history corrections raised it to `504` passing
tests with `81%` total branch coverage. The version 1.0 documentation and
identity closeout adds four tests for an expected total of `508`.

The release-readiness evidence includes:

- Clean installation, first-use workflows, and relaunch persistence.
- `v0.3.0` and `v0.7.0` database-fixture upgrades.
- Backup round trips, rejected restores, Clear All Data, reinstall, and
  recovery.
- Exact controlled totals and a 10,000-transaction scale profile.
- Virtualized history rendering and stable recycled-card row heights.
- Narrow, larger-phone, and 200% enlarged-font profiles.
- Accessibility, keyboard, Android Back, and destructive-confirmation
  behavior.

The final `v1.0.0` gate additionally requires a green complete suite and
GitHub Actions run, real Settings screenshot, verified signed artifact, clean
installation, and official in-place upgrade from `v0.8.0`.

## Update 1 Account-Transfer Regression

Update 1 adds focused coverage for:

- migration 5, repeat runs, rollback, constraints, foreign keys, indexes, and
  upgrades from the released migration-4 schema;
- exact transfer CRUD, stable ordering, source/destination queries, and named
  transfer records;
- form-state transitions and service validation for distinct accounts,
  positive integer-centavo amounts, missing records, and database failures;
- transfer-screen navigation, Back behavior, account selectors, reusable
  amount/date/time/notes controls, responsive layout, and enlarged fonts;
- per-account outgoing/incoming balance effects, all-account net zero,
  Income/Expenses exclusion, unified activity ordering, search, filters,
  edit/delete/undo, and large-history behavior;
- backup format 2 export, strict validation, replacement restore, record
  counts, ID sequences, integrity checks, Clear All Data, and late-failure
  rollback;
- compatibility restore of format-1 v1.0 backups with zero transfers; and
- protection against deleting accounts referenced by a transfer.

Every implementation checkpoint passed its focused Windows and
real-application gate before commit. The final v1.1.0 gate still requires the
complete suite with coverage, compilation, whitespace validation, green
GitHub Actions, a signed Android build, clean installation, and an official
in-place v1.0.0-to-v1.1.0 upgrade using controlled transfer data.

## GitHub Actions

`.github/workflows/quality.yml` runs on pushes, pull requests, and manual
workflow requests.

The workflow:

1. Uses a Windows runner.
2. Installs Python 3.13.14.
3. Installs `requirements-dev.txt`.
4. Compiles the Python source.
5. Runs the complete test suite with coverage.

The hosted Windows runner exposes only OpenGL 1.1, while Kivy requires
OpenGL 2.0 for real rendering. The workflow therefore uses Kivy's mock
graphics backend for headless tests. This setting exists only inside the
workflow and does not change desktop or Android rendering.

## Expected Results

A change is ready for checkpoint review when:

- Every collected test passes.
- Coverage collection finishes successfully.
- Compilation produces no errors.
- `git diff --check` produces no output.
- `git status --short` shows only intended files.
- Any relevant desktop or Android behavior check passes.
- GitHub Actions becomes green after the change is pushed.

The number of tests will increase as the project grows. Success depends on
all collected tests passing, not on preserving a fixed count.

## Before Committing

1. Review the intended changed files.
2. Run the required local checks.
3. Perform any real-application check relevant to the change.
4. Commit the verified checkpoint.
5. Push the branch and confirm that GitHub Actions passes.

## Update 2 Pending-Transaction Contract Baseline

Update 2 began from the clean released `v1.1.0` baseline on the
`update-2-pending-transactions` branch. Before migration or feature code was
changed, the complete Windows suite reported `637 passed` with `83%` total
branch coverage on Python `3.13.14`.

The Task 1 contract regression is maintained in
`tests/test_update2_contract.py`. It verifies the non-posting calculation
contract, status and migration direction, activity/filter behavior, backup
compatibility, weighted checkpoint evidence, and the explicitly carried
Android upgrade exception.

Task 1 changes documentation and contract tests only. Migration, repository,
service, UI, and recovery behavior must not be implemented until the contract
checkpoint passes and is committed.

## Update 2 Status-Aware Persistence Regression

Task 2 adds focused persistence coverage for migration 6, the constrained
`posting_status` column, default-posted legacy upgrades, status-aware records
and CRUD, compare-and-set posting, status-preserving restore, posted-only
financial totals, and account/category deletion protection for temporary
references.

The 10,000-record history regression now seeds both posted and temporary rows.
It proves that a status-filtered newest-first query uses
`transactions_posting_status_history_index` and does not create a temporary
B-tree for ordering. The index is intentionally limited to posting status,
date, and ID; additional account/category status indexes require their own
query-plan evidence.

Task 2 completed with `654 passed`, `83%` total branch coverage, successful
Python compilation, and a clean Git whitespace check. It changed no visible
screen or workflow, so its checkpoint required no real-application check.

### Update 2 Task 3A pending save/edit workflow gate

Task 3A extends form state and the transaction service without adding visible
controls. Run the focused gate below before the complete suite:

```bat
python -m pytest -q ^
tests/test_transaction_form_state.py ^
tests/test_transaction_payload.py ^
tests/test_transaction_validation.py ^
tests/test_transaction_services.py ^
tests/test_temporary_transaction_save_workflows.py ^
tests/test_temporary_transaction_persistence.py
```

The focused gate contains `61` tests. It verifies explicit pending creation,
exact centavo payloads, status-preserving edits, invalid-status and date/time
rejection, missing-record behavior, and stable repository-failure results. The
complete Task 3A gate is expected to report `666 passed` with approximately
`83%` total branch coverage.

### Update 2 Task 3B posting and recovery workflow gate

Task 3B completes the UI-independent transaction service workflow without
adding visible controls. Run the focused gate below before the complete suite:

```bat
python -m pytest -q ^
tests/test_transaction_services.py ^
tests/test_temporary_transaction_save_workflows.py ^
tests/test_temporary_transaction_post_workflows.py ^
tests/test_temporary_transaction_persistence.py ^
tests/test_transaction_repository.py ^
tests/test_transfer_balances.py
```

The focused gate contains `89` tests. It verifies compare-and-set posting,
exact-centavo total changes, repeated-post prevention, missing-record behavior,
induced database-failure rollback, status-preserving delete/restore, and stable
repository-exception results. The complete Task 3 gate is expected to report
`682 passed` with approximately `83%` total branch coverage. Because the
checkpoint introduces no visible control, no real-application check is required.


### Update 2 Task 4A transaction-form interface gate

Task 4A exposes the verified pending save and posting services through the
transaction form. Run this focused gate before the complete suite:

```bat
python -m pytest -q ^
tests/test_transaction_form_actions.py ^
tests/test_transaction_form_state.py ^
tests/test_transaction_screen_workflows.py ^
tests/test_responsive_layout.py ^
tests/test_accessibility_semantics.py
```

The focused gate contains `82` tests. It verifies explicit pending and posted
actions, current-field validation before posting an edited pending record,
failed-save and failed-post preservation, posted-record reversal protection,
dynamic titles and status text, responsive stacking, enlarged-font growth, and
non-color-only semantics. The complete Task 4A gate is expected to report `696
passed` with approximately `83%` total branch coverage.

Because Task 4A changes visible behavior, also perform these real-application
checks before committing:

1. Open a new transaction and confirm both text actions are visible.
2. Save an expense as pending and confirm Dashboard balance, Income, and
   Expenses do not change.
3. Reopen that record and confirm the title and visible status say Pending.
4. Edit its amount or notes, post it, and confirm the exact financial effect is
   applied once.
5. Reopen a posted record and confirm the secondary action reads `Already
   Posted` and is disabled.
6. Check the action group on a narrow window and with enlarged system text.

### Update 2 Task 4B activity-card interface gate

Task 4B carries posting status through unified Activity records and exposes the
verified posting workflow from Dashboard recent activity and virtualized
Activity History. Run this focused gate before the complete suite:

```bat
python -m pytest -q ^
tests/test_activity_repository.py ^
tests/test_database_records.py ^
tests/test_transaction_list.py ^
tests/test_transaction_list_actions.py ^
tests/test_responsive_layout.py ^
tests/test_accessibility_semantics.py ^
tests/test_overlay_components.py ^
tests/test_update2_contract.py
```

The gate verifies that pending records keep their status in unified activity,
transfers retain the posted-only shared card contract, recycled cards reset all
status properties, and only pending transaction cards expose posting. It also
covers financial-effect confirmation copy, temporary-specific deletion copy,
Dashboard summary refresh, virtualized-list refresh, non-color-only status
semantics, font-scaled card height, and use of the shared custom overlay.

The complete Task 4 gate is expected to report `707 passed` with approximately
`83%` total branch coverage. Because this checkpoint changes visible activity
behavior, also perform these real-application checks before committing:

1. Save a recognizable expense as temporary and confirm Dashboard recent
   activity shows a clock icon and `PENDING` text.
2. Open Activity History and confirm the same record has the same status and
   edit, post, and delete actions.
3. Open the post confirmation and verify it warns that balances and totals will
   update immediately; cancel and confirm nothing changes.
4. Post the record from the card, then confirm the Pending treatment and post
   action disappear and the exact Dashboard balance and Expense change occurs
   once.
5. Attempt the stale action again only if an old view remains visible; confirm
   the service rejects repeated posting without a second financial effect.
6. Delete and undo-restore a pending record and confirm its Pending status
   returns and totals remain unchanged.
7. Check Dashboard and Activity History on a narrow window and enlarged system
   text; card content and all actions must remain readable without clipping.

## Update 2 Task 7A Release-Candidate Gate

Task 7A prepares the v1.2.0 source release identity before the Android artifact
is built. The gate verifies:

- `main.py`, README, changelog, roadmap candidate identity, release guide, and
  candidate release notes agree on `1.2.0`;
- Pending Transactions, migration 6, backup format 3, and older-format
  normalization are documented consistently;
- the Android checklist requires the official v1.1.0-to-v1.2.0 upgrade and
  controlled posted/Pending checks;
- release-note evidence that depends on CI, signing, installation, upgrade, or
  the generated APK remains explicitly pending rather than guessed; and
- the complete suite, coverage, compilation, and whitespace checks pass.

Task 7B replaces every pending release-evidence field only after the signed APK
and physical-device checks provide the actual values.

## Update 3 Pass-through Transfer Contract Baseline

Update 3 begins from the clean released `v1.2.0` baseline on the
`update-3-pass-through-transfers` branch. Before migration or feature code is
changed, the complete Windows suite reported `746 passed in 32.69s` with `83%`
total branch coverage on Python `3.13.14`.

The Task 1 contract regression is maintained in `tests/test_update3_contract.py`.
It locks the Cash-to-Bank direction, exact net-zero financial invariants,
Internal-versus-Pass-through compatibility, optional counterparty and separate
fee handling, activity/filter behavior, migration 7 direction, backup format 4
compatibility, and the 100%-weighted checkpoint plan.

Task 1 changes documentation and contract tests only. Migration 7, repository,
service, UI, activity, and recovery implementation must wait until this contract
checkpoint passes and is committed.


### Update 3 Task 2 migration and persistence gate

Task 2 extends the existing account-transfer ledger instead of creating a
second financial subsystem. Run the focused persistence gate before the
complete suite:

```bat
python -m pytest -q ^
tests/test_pass_through_transfer_persistence.py ^
tests/test_transfer_repository.py ^
tests/test_transfer_services.py ^
tests/test_transfer_balances.py ^
tests/test_migrations.py ^
tests/test_phase9_migrations.py ^
tests/test_recovery_contract.py ^
tests/test_backup_exporter.py ^
tests/test_backup_restorer.py ^
tests/test_backup_validator.py ^
tests/test_pending_backup_recovery.py
```

The gate verifies migration 7 defaults and constraints, legacy Internal
compatibility, exact transfer-kind persistence, trimmed/blank counterparty
normalization, invalid-kind rejection, stable newest-first ordering, combined
account/kind repository filtering, edit/delete/undo restoration, migration
repeat-run and rollback behavior, unchanged legacy financial totals, recovery
schema history, and continued format-3 development compatibility with database
version 7.

No dedicated `transfer_kind` index is expected at this checkpoint. Query-plan
coverage confirms the existing `account_transfers_history_order_index` remains
the ordering access path; later activity/filter work may add an index only if
its real query plans justify one.

After the focused gate, run the complete suite and branch coverage, Python
compilation, and `git diff --check`. Task 2 changes persistence only and does not
yet expose Pass-through controls in the real application, so no manual UI gate
is required before this checkpoint commit.


### Update 3 Task 3 pass-through service workflow gate

Task 3 extends the existing transfer service and form-state path without adding
visible Pass-through controls yet. Run this focused gate before the complete
suite:

```bat
python -m pytest -q ^
tests/test_pass_through_transfer_workflows.py ^
tests/test_transfer_services.py ^
tests/test_transfer_form_state.py ^
tests/test_transfer_screen_workflows.py ^
tests/test_transfer_balances.py ^
tests/test_pass_through_transfer_persistence.py
```

The gate verifies exact-centavo create/edit/delete/restore behavior, canonical
Cash-to-Bank effects, all-account net-zero invariants, unchanged Income and
Expense totals, same-account and metadata validation, stable repository-failure
results, preserved Pass-through kind/counterparty during edit state, and legacy
Internal-transfer defaults.

After the focused gate, run the complete suite with branch coverage, Python
compilation, and `git diff --check`. Task 3 changes workflows/state only; the
real-app transfer-mode and counterparty controls belong to Task 4.


### Update 3 Task 4 pass-through interface gate

Task 4 exposes Pass-through controls on the existing Transfer screen. Run this
focused gate before the complete suite:

```bat
python -m pytest -q ^
tests/test_transfer_screen_workflows.py ^
tests/test_transfer_form_state.py ^
tests/test_pass_through_transfer_workflows.py ^
tests/test_transfer_services.py ^
tests/test_responsive_layout.py ^
tests/test_accessibility_semantics.py
```

The gate verifies explicit Internal-versus-Pass-through selection, canonical
FROM/TO direction guidance, `Cash → Bank` copy for the cash-out example,
Pass-through-only optional counterparty entry, metadata preservation while
editing, Internal metadata cleanup, responsive mode stacking, font-scaled touch
targets, and non-color-only text cues.

After the focused gate, run the complete suite with branch coverage, Python
compilation, and `git diff --check`. Because Task 4 changes visible behavior,
also complete this short real-app gate before committing:

1. Open Transfer and confirm `INTERNAL` is selected by default and the
   counterparty control is hidden.
2. Select `PASS-THROUGH`; confirm the visible copy says FROM decreases, TO
   increases, includes the `Cash → Bank` example, and states the principal is
   not Income or Expense.
3. Enter an optional counterparty, select Cash as FROM and Bank as TO, save a
   small controlled amount, then reopen it for editing and confirm kind,
   direction, counterparty, amount, date/time, and notes are preserved.
4. Check the form at a narrow phone-sized window and with enlarged system text;
   the mode buttons must stack when constrained, guidance must wrap without
   clipping, and the counterparty row must remain usable.

Task 4 does not yet add Activity History labels/search/filters; those belong to
Task 5.


### Update 3 Task 5 activity, search, and filter gate

Task 5 integrates Pass-through records into unified activity while preserving
all financial invariants. Run this focused gate before the complete suite:

```bat
python -m pytest -q ^
tests/test_activity_repository.py ^
tests/test_activity_services.py ^
tests/test_transaction_filter_state.py ^
tests/test_transaction_list.py ^
tests/test_transaction_list_actions.py ^
tests/test_transaction_screen_workflows.py ^
tests/test_pending_activity_integration.py ^
tests/test_transfer_balances.py ^
tests/test_responsive_layout.py ^
tests/test_accessibility_semantics.py
```

The gate verifies that the general Transfer filter includes both transfer kinds,
Advanced Filters split Internal and Pass-through, counterparty/kind text is
searchable, account/date filters compose with kind, newest-first ordering is
stable, Dashboard and Activity History share visible Pass-through card semantics,
and recycled cards do not retain stale kind/counterparty state. Existing posted
Income, posted Expenses, Pending behavior, and transfer-aware account balances
must remain unchanged.

The UI portability check also requires plain `Cash to Bank` wording and an ASCII
` | ` active-filter separator instead of decorative arrow/bullet glyphs. Currency
formatting remains unchanged because the peso symbol is part of the app's money
presentation contract.

After the focused gate, run the complete suite with branch coverage, Python
compilation, and `git diff --check`. Then complete this short real-app gate:

1. Create one Internal and one Pass-through transfer with recognizable notes;
   give the Pass-through record a counterparty.
2. Confirm Dashboard recent activity and Activity History show the Pass-through
   record with visible `PASS-THROUGH` text and `Cash to Bank` style direction.
3. Confirm primary `TRANSFER` shows both records; Advanced `INTERNAL` shows only
   Internal and Advanced `PASS-THROUGH` shows only Pass-through.
4. Search by counterparty and by `pass-through`; confirm only the expected record
   matches. Combine Pass-through with an account and date filter once.
5. Confirm Income, Expenses, category totals, and all-account balance do not
   change from the Pass-through principal; only the two participating account
   balances move equally and oppositely.
6. Edit, delete, undo, and switch filters once; confirm labels refresh without a
   recycled card showing stale Internal/Pass-through metadata.


### Update 3 Task 6 backup, recovery, and performance gate

Task 6 raises new exports to backup format 4 and makes Pass-through metadata
release-safe. Run this focused gate before the complete suite:

```bat
python -m pytest -q ^
tests/test_backup_format.py ^
tests/test_backup_exporter.py ^
tests/test_backup_validator.py ^
tests/test_backup_restorer.py ^
tests/test_pending_backup_recovery.py ^
tests/test_pass_through_backup_recovery.py ^
tests/test_recovery_contract.py ^
tests/test_document_transfer.py ^
tests/test_settings_screen_workflows.py ^
tests/test_update2_contract.py ^
tests/test_update3_contract.py
```

The gate verifies exact format-4 `transfer_kind`/`counterparty` export and
restore, preserved Pending/posting status, format-1 empty-transfer behavior,
format-2 and format-3 transfer normalization to Internal, malformed current-kind
and counterparty rejection before replacement, record counts, IDs, sequences,
foreign keys, integrity, Clear All Data, document-transfer compatibility, and a
10,000-transfer mixed-history round trip.

The large-history plan must continue using
`account_transfers_history_order_index` for newest-first Pass-through access
without `USE TEMP B-TREE FOR ORDER BY`. Do not add a transfer-kind index unless
the measured plan demonstrates a regression that the index fixes.

After the focused gate, run the complete suite with branch coverage, Python
compilation, and `git diff --check`. Then complete one short real-app recovery
gate before committing:

1. Keep one posted transaction, one Pending transaction, one Internal transfer,
   and one Pass-through transfer with a counterparty. Record both account
   balances plus Income and Expenses.
2. Export the backup. Restore preview must show the expected record counts.
3. Clear All Data using the normal Settings workflow, then restore the export.
4. Confirm Internal remains Internal; Pass-through remains Pass-through; its
   counterparty, amount, direction, date/time, and notes are exact.
5. Confirm Pending remains Pending and posted remains posted.
6. Confirm both account balances, all-account balance, Income, and Expenses match
   the values recorded before export. Relaunch once and verify the same state.
