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
