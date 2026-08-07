# Enkryon Development Roadmap

Updated: August 6, 2026
Current release: `v1.2.0`
Next planned release: `v1.3.0`
Current position: Update 2 Pending Transactions passed its complete automated,
signed-Android, clean-install, official v1.1.0-to-v1.2.0 upgrade, and format-3
recovery gates. Merge, tag, and GitHub Release publication remain.

## Purpose

This roadmap records Enkryon's completed version 1.0 foundation and guides
the backward-compatible version 1.x feature updates built on it.

The phases are ordered by risk. Enkryon must first protect financial data, calculate money exactly, catch defects automatically, and survive app upgrades. Only after that foundation is dependable should the project add major features such as reports, budgets, recurring transactions, or cloud synchronization.

## Status Guide

| Status | Meaning |
|---|---|
| Completed | The objective was implemented and verified. |
| Next | This is the immediate development priority. |
| Partially completed | Some work is already proven, but the phase still has required items. |
| Planned | The phase has not started in a focused way. |
| Deferred | Do not begin this work until its prerequisite release is stable. |

## Current Project Snapshot

| Area | Current project state | What it means for the roadmap |
|---|---|---|
| Core product | Accounts, categories, posted income and expenses, Pending Transactions, first-class account transfers, editing, deletion/undo, dashboard totals, unified activity history, collapsible advanced filters, and local storage are implemented. | Add pass-through transfers next without weakening posted/Pending financial semantics. |
| Financial accuracy | Transaction and transfer amounts remain integer centavos; per-account transfers are directional while the all-account balance, Income, and Expenses remain unchanged. | Transfer movement stays separate from earned income and spending. |
| Database upgrades | A `schema_migrations` table and six ordered, transactional migrations are present; migration 6 adds constrained transaction posting status and its newest-first status-history index. | Automated migration and query-plan coverage passed; the waived official v1.0.0-to-v1.1.0 Android upgrade remains explicitly unverified. |
| Data rules | The database rejects invalid transaction and transfer amounts, invalid dates, same-account transfers, invalid transaction types, blank or untrimmed names, duplicates, and missing relationships. Foreign keys remain enabled. | Important data rules are enforced even if a screen-level check is missed. |
| Automated tests | The released v1.1.0 baseline contained `637` passing tests with `83%` total coverage; the final v1.2.0 release gate contains `746` passing tests at `83%` total branch coverage. | Keep the same focused-test, complete-suite, compilation, whitespace, CI, and device gates for v1.3.0. |
| Android release | The permanently signed `v1.2.0` artifact passed checksum, signature, alignment, clean-install, package-identity, official v1.1.0-to-v1.2.0 upgrade, Pending workflow, backup/restore, and relaunch checks. The older v1.0.0-to-v1.1.0 waiver remains historical. | Publish v1.2.0, continue recommending a pre-upgrade backup, and preserve the permanent signing identity for v1.3.0. |
| Architecture | Focused transfer components, status-aware persistence, UI-independent pending workflows, explicit form actions, and status-aware activity/filter records now feed the existing service boundaries. | Keep backup validation and restore rules in the recovery layer without moving SQL or posting rules into UI code. |
| User experience | The transaction form, activity cards, Dashboard, and Activity History expose non-color-only Pending status, guarded posting, explicit Pending filtering, and posted-only Income/Expense views. | Preserve these semantics through backup, restore, relaunch, and Android upgrade checks. |
| Backup and recovery | Backup format 3 preserves transaction posting status and transfers; format-1 and format-2 documents normalize their transactions to posted before replacement restore. | Preserve this compatibility through release regression and the official v1.1.0-to-v1.2.0 upgrade. |
| Search and advanced filters | Unified activity search and filters cover posted Income, posted Expenses, Transfers, Pending records, accounts, notes, groups, categories, and inclusive dates with stable newest-first ordering. | Preserve exact status and filter behavior through backup format 3 and release regression. |

## Phase Overview

| Phase | Plain-language objective | Status |
|---|---|---|
| 1. Safe Foundation and Consistent Design | Make the existing app safer, easier to maintain, and visually consistent. | Completed |
| 2. Exact Money and Safe Database Upgrades | Prevent rounding errors and upgrade existing databases without losing data. | Completed |
| 3. Automatic Quality Checks | Test every change automatically so defects are caught before release. | Completed |
| 4. Reliable Android Releases | Make Android builds repeatable, correctly signed, clearly versioned, and safe to install as upgrades. | Completed |
| 5. Simpler, More Maintainable Code | Move business rules out of large screens and give each code layer one clear job. | Completed |
| 6. Clear, Accessible, Responsive User Experience | Make all existing workflows comfortable and understandable across supported phones. | Completed |
| 7. Backup, Restore, and Recovery | Let users preserve and recover their local financial records safely. | Completed |
| 8. Transaction Search and Advanced Filters | Help users find specific transactions quickly, even in large histories. | Completed |
| 9. Beta Testing and Version 1.0 Readiness | Prove that the complete core app is stable enough for a version 1.0 release. | Completed |
| 10. Version 1.x Feature Expansion | Add transfers, statistics, and later financial capabilities without weakening the stable core. | In progress |

---

## Phase 1 — Safe Foundation and Consistent Design

**Status:** Completed

### Objective

Make the existing application safe enough to improve: document its behavior, repair serious defects, separate code responsibilities, protect the database, and apply one consistent visual identity.

### Completed work

#### 1.1 Baseline and critical repairs

- Tested the clean first-use flow and documented existing behavior.
- Protected accounts and categories that are already used by transactions.
- Prevented orphaned transaction records through foreign keys and deletion rules.
- Fixed large-amount display problems.
- Refreshed dashboard information after account and category changes.
- Standardized duplicate-name validation.
- Added reusable empty states.

#### 1.2 Architecture and database safety

- Defined the responsibilities of screens, services, repositories, widgets, utilities, and theme modules.
- Moved the runtime database to the app's user-data directory.
- Excluded local database files from source control and Android packaging.
- Removed user-interface behavior from transaction services.
- Extracted reusable amount, validation, date/time, and transaction-payload helpers.
- Added repository and helper tests.
- Built and smoke-tested an Android APK.

#### 1.3 Design system

- Documented the emerald-and-gold brand direction.
- Added shared color, spacing, radius, typography, size, and elevation values.
- Applied the visual direction to the existing screens.
- Added reusable primary, secondary, and filter buttons.
- Standardized selected states and empty-state styling.

### Documentation status

Phase 3 updated the old Phase 1.2 summary so resolved observations are no
longer presented as current defects.

### Completion gate

**Passed.** The app has a documented structure, safer local storage, reusable design foundations, and regression tests that allowed the financial-correctness work to proceed.

---

## Phase 2 — Exact Money and Safe Database Upgrades

**Status:** Completed in `v0.4.0`
**Priority achieved:** Critical

### Objective

Make all financial values exact and ensure that users can move from an older Enkryon database to a newer one without losing records or receiving partially applied changes.

### Completed work

1. Added one database startup path that creates tables in dependency order: accounts, category groups, categories, then transactions.
2. Added a versioned migration runner and a `schema_migrations` history table.
3. Made migrations run inside a database transaction so a failure rolls back the whole migration attempt.
4. Made migrations safe to run again: completed versions are not repeated.
5. Converted transaction values from decimal `amount` storage to integer `amount_centavos` storage.
6. Added exact conversion and display helpers for pesos and centavos.
7. Updated transaction input, saving, editing, totals, balances, and display formatting to use centavos.
8. Added database rules for positive whole-centavo amounts, valid date/time values, valid transaction types, required relationships, trimmed non-empty names, and normalized duplicate names.
9. Unified the application version at `0.4.0`; Buildozer and the README now read or reflect the same value.
10. Added tests for migration order, repeat runs, rollback behavior, exact conversion, database constraints, and version consistency.
11. Built and verified the signed `v0.4.0` Android APK.

### Verification evidence recorded in the ZIP

- `88` automated tests passed.
- Existing transaction IDs, row counts, totals, and relationships were preserved during the legacy upgrade test.
- Failed migrations rolled back cleanly.
- The APK passed `apksigner` verification.
- The APK passed `zipalign` verification.
- A clean Android installation and centavo-transaction smoke test passed.
- The release uses Enkryon's permanent signing certificate.

### Important upgrade note

Earlier debug-signed builds cannot be upgraded directly to `v0.4.0` because they used a different signing identity. Those installations require a clean reinstall. Starting with `v0.4.0`, future releases should use the same permanent certificate so normal in-place upgrades can be tested and supported.

### Documentation status

Phase 3 expanded the database guide, repaired the Phase 2 verification
report, and updated the stale Phase 1.2 follow-up list.

### Completion gate

**Passed.** Financial values use exact centavos, old data has a tested upgrade path, failed migrations are recoverable, repeat runs are safe, database rules are enforced, and release version values agree.

---

## Phase 3 — Automatic Quality Checks

**Status:** Completed
**Priority achieved:** High

### Objective

Run the same dependable checks for every proposed change so a broken migration, calculation, or core workflow is discovered before it becomes a release.

### Completed work

#### 3.1 Reproducible development setup

- Added `requirements-dev.txt` without placing test tools in the Android
  runtime dependencies.
- Pinned pytest and pytest-cov to the versions verified during the phase.
- Documented the verified Python environment and required local commands.

#### 3.2 GitHub Actions

- Added automatic checks for pushes, pull requests, and manual runs.
- Used Python 3.13.14 on a fresh Windows runner.
- Added dependency caching, source compilation, tests, and coverage output.
- Used Kivy's mock graphics backend because the hosted runner exposes
  OpenGL 1.1 rather than the OpenGL 2.0 required for real rendering.
- Verified repeated green runs after resolving the initial headless
  graphics failure.

#### 3.3 Stronger correctness evidence

- Added a saved `v0.3.0` SQLite fixture with legacy `REAL` amounts.
- Verified that all three migrations preserve record counts, transaction
  IDs, relationships, exact centavo values, totals, and balance.
- Verified that rerunning the migration framework does not change data.
- Added transaction-service success and failure-path tests.
- Preserved repository deletion results through the service boundary.
- Added a headless application-import smoke test for all six screens.
- Established an initial `51%` application-wide branch-coverage baseline.

#### 3.4 Documentation cleanup

- Corrected the stale Phase 1.2 follow-up list.
- Expanded the database architecture and migration guide.
- Repaired the Phase 2 verification report formatting.
- Added local testing and coverage instructions.
- Added this roadmap to the repository and linked it from the README.

### Deliverables

- Reproducible development/test dependency setup. **Completed**
- GitHub Actions workflow for pushes and pull requests. **Completed**
- Automatic compilation, test, and coverage results. **Completed**
- Old-version database fixture and upgrade test. **Completed**
- Service and failure-path tests. **Completed**
- Headless application import smoke test. **Completed**
- Clear local testing instructions. **Completed**
- Corrected Phase 1 and Phase 2 documentation. **Completed**

### Verification evidence

- `99` automated tests passed locally and in GitHub Actions.
- Application-wide branch coverage measured `51%`.
- Python compilation completed without errors.
- Git whitespace checks passed.
- The working tree was clean before closeout.
- The desktop navigation smoke check passed for Dashboard, Accounts,
  Categories, Add Transaction, Transaction History, and Settings.

### Known limits carried forward

- Screen and interactive-widget behavior has lower coverage than the
  financial and migration layers. Deeper UI testing belongs to Phase 6.
- Phase 3 records coverage but does not impose an arbitrary percentage
  threshold.
- Transaction creation and editing still live mainly in screen code and
  are assigned to Phase 5 architecture work.
- Android build and upgrade automation remains Phase 4 work.

### Completion gate

**Passed.** The pinned environment works locally and on fresh GitHub
runners, pushes and pull requests receive automatic checks, the saved
legacy database upgrades without data loss, failures produce a red check,
and the full regression and desktop smoke checks pass.

---

## Phase 4 — Reliable Android Releases

**Status:** Completed in `v0.4.8`
**Priority achieved:** High

### Objective

Produce Android releases that are repeatable, correctly signed, appropriately packaged, clearly documented, and safe to install over the previous official release.

### Completed work

1. Pinned the Android API, minimum API, NDK, NDK API, Buildozer, Cython,
   and Python-for-Android compatibility versions.
2. Documented the reproducible WSL build environment and separate debug
   and release procedures.
3. Added secure release-signing instructions and a helper that keeps keys
   and passwords outside the repository.
4. Added adaptive launcher assets and verified their packaged resources on
   a physical Android device.
5. Removed duplicated screenshots, icons, and splash sources from the APK,
   reducing the verified candidate to 45,767,240 bytes.
6. Standardized release artifact names, checksum sidecars, changelog
   entries, release notes, and the Android release checklist.
7. Added automated tests for build settings, signing rules, packaging,
   assets, version extraction, certificate parsing, and release records.
8. Explicitly disabled Android auto-backup until Phase 7 provides a
   user-controlled, validated backup and restore flow.
9. Built `Enkryon-v0.4.8.apk` with the permanent Enkryon certificate and
   verified its checksum, signature, alignment, API levels, ABIs, backup
   policy, and package exclusions.
10. Installed `v0.4.8` over official `v0.4.0` with `adb install -r` and
    confirmed that all controlled records, exact totals, and notes survived.
11. Created a post-upgrade transaction and confirmed that it persisted
    after the upgraded application was closed and relaunched.

### Deliverables

- Explicit and reviewed Android build settings. **Completed**
- Debug and release build instructions. **Completed**
- Secure signing instructions. **Completed**
- Optimized/adaptive application icon assets. **Completed**
- Standard artifact, checksum, changelog, and release-note process.
  **Completed**
- Android release checklist. **Completed**
- Successful in-place upgrade evidence from `v0.4.0`. **Completed**

### Verification evidence

- `125` automated tests passed locally and in GitHub Actions.
- Python compilation and Git whitespace checks passed.
- `Enkryon-v0.4.8.apk` matched its SHA-256 checksum sidecar.
- The APK contained no repository screenshots, source icons, source splash
  assets, tests, documentation, databases, caches, or signing keys.
- The APK used the permanent Enkryon certificate and passed `apksigner` and
  `zipalign` verification.
- The official-to-official upgrade preserved the controlled financial
  dataset and accepted a persistent post-upgrade transaction.
- Detailed evidence is recorded in
  `docs/audits/phase-4-upgrade-verification.md` and
  `docs/audits/phase-4-verification.md`.

### Known limits carried forward

- Automatic Android backup remains disabled. Phase 7 will provide an
  explicit, validated backup and restore flow.
- The APK contains both supported native architectures and their runtime
  libraries; further size reduction must not compromise compatibility.
- Broader device, font-size, accessibility, and layout testing belongs to
  Phase 6.
- Large screen controllers and remaining business logic move to Phase 5.

### Completion gate

**Passed.** Another developer can reproduce the documented build, the
artifact contains no development-only files, signature and alignment checks
pass, and permanently signed `v0.4.8` installs over official `v0.4.0`
without losing user data.

---

## Phase 5 — Simpler, More Maintainable Code

**Status:** Completed
**Priority:** Medium-high

### Objective

Make changes safer by moving business rules out of large screen files and giving screens, services, repositories, utilities, and widgets one clear responsibility each.

### Completed work

1. Added characterization tests around transaction, account, category, and settings screen workflows before changing their architecture.
2. Replaced positional database tuples with named account, category-group, category, transaction, and transaction-detail records.
3. Moved transaction validation, payload construction, creation, editing, deletion, and view preparation behind transaction services.
4. Extracted explicit transaction form state and centralized its dependent selection transitions.
5. Added account and category services that normalize input and translate repository outcomes into clear action results.
6. Added context-managed database connections with rollback, close, foreign-key, and failure-path tests.
7. Standardized repository write outcomes for duplicates, referenced records, missing records, validation failures, and database failures.
8. Consolidated shared transaction filtering, editing, deletion, confirmation dialogs, refresh behavior, and action-result rendering.
9. Expanded the behavior-preserving suite from `125` tests at the Phase 5 baseline to `252` tests at closeout.
10. Recorded the completed boundaries and evidence in the architecture guide and Phase 5 verification report.

### Deliverables

- Smaller screen controllers.
- Complete service boundaries for transaction workflows.
- Consistent repository results and errors.
- Named data objects between the database and interface layers.
- Updated architecture documentation and tests.

### Completion gate

**Passed.** Screens coordinate interface state instead of owning financial or persistence rules, core workflows are tested without rendering the interface, repository and service failures have explicit meanings, and repeated transaction-list and action-result behavior has one maintained implementation.

---

## Phase 6 — Clear, Accessible, Responsive User Experience

**Status:** Completed
**Priority achieved:** Medium-high

### Objective

Make every existing workflow understandable and comfortable on supported
Android phones, including small screens, large text, long names, empty data,
and error situations.

### Completed work

1. Exercised first-use, populated, empty, validation-error, and destructive
   states across the existing screens.
2. Preserved unfinished transaction form values when users temporarily
   navigate to account or category management.
3. Improved Dashboard information hierarchy, account filtering, scrolling,
   summary-value layout, and large-balance presentation.
4. Improved transaction-card alignment, amount emphasis, long-content
   behavior, and action placement.
5. Added responsive rules and regression tests for narrow layouts, enlarged
   text, scrolling, fixed controls, and content-height boundaries.
6. Made income and expense states identifiable through text and visual
   treatment instead of color alone.
7. Added useful next-step actions to empty states.
8. Added About, version, local-data, and privacy information to Settings.
9. Replaced selection, input, and confirmation workflows with reusable
   customized card-based overlays.
10. Standardized overlay sizing, option selection, scrolling, keyboard
    behavior, floating labels, cancellation, and destructive confirmation.
11. Made Android Back and desktop Escape dismiss the active overlay before
    underlying navigation.
12. Expanded the automated suite from the `252`-test Phase 6 baseline to
    `391` implementation tests and `395` tests after documentation closeout.

### Deliverables

- Screen-by-screen user-experience regression checklist.
- Supported-profile and font-size test conditions.
- Accessibility, selection-state, contrast, and touch-target checks.
- Improved Dashboard, transaction cards, navigation, and empty states.
- Customized card-based selectors, input dialogs, and confirmation prompts.
- Updated Settings information.
- Phase 6 verification report and closeout tests.

### Release follow-up item

Repository screenshot replacement is outside the Phase 6 completion gate and
should use the final packaged `v0.6.0` build when performed.

### Completion gate

**Passed.** Core workflows were checked through automated layout and behavior
tests plus relevant small-screen, larger-screen, enlarged-font, Android, and
desktop application checks. Navigation preserves expected state, destructive
actions remain recoverable, active overlays receive Back priority, and the
primary balance remains readable through the supported display boundary.

The exhaustive manual matrix was not repeated after every final correction.
That explicit evidence limit and the accepted constrained-card amount
shortening are recorded in the Phase 6 verification report.

---

## Phase 7 — Backup, Restore, and Recovery

**Status:** Completed in `v0.7.0`
**Priority achieved:** High before leaving alpha

### Objective

Give users a safe, understandable way to preserve and recover their local financial records before clearing data, changing devices, or installing risky upgrades.

### Completed work

1. Defined a versioned JSON backup format with application, database,
   export-date, and record-count metadata.
2. Exported accounts, category groups, categories, and transactions while
   preserving IDs, relationships, dates, notes, names, and integer-centavo
   values.
3. Added complete validation before restore can modify the current database.
4. Added confirmed replacement restore inside a database transaction, with
   rollback on failure.
5. Added restore previews showing backup version, export date, and record
   counts.
6. Added Android document-picker export and import without requesting broad
   storage permission.
7. Added clear failure and cancellation handling for malformed,
   incompatible, corrupted, or unavailable backups.
8. Added a two-stage Clear All Data flow that offers backup before the final
   deletion confirmation.
9. Verified backup, replacement restore, clearing, and recovery on Android.

### Deliverables

- Local backup/export flow.
- Validated restore/import flow.
- Corruption and incompatibility handling.
- Round-trip and failure-path tests.
- User-facing recovery instructions.

### Completion gate

**Passed.** A populated database was exported, cleared, restored, and
verified without changing balances, relationships, dates, notes, names,
transaction IDs, or integer-centavo values.

Restore in `v0.7.0` intentionally replaces existing application data.
Merging backups is deferred until after statistics. Cloud synchronization
remains outside this phase.

---

## Phase 8 — Transaction Search and Advanced Filters

**Status:** Completed in `v0.8.0`
**Priority achieved:** Medium

### Objective

Help users quickly find a specific transaction by its text, account, category, type, or date—even when the history becomes large.

### Completed work

1. Added search across notes, account names, category-group names, and category names.
2. Added filters for account, transaction type, category group, category, and inclusive date range.
3. Made every search and filter option work alone and in combination.
4. Added active-filter summaries and a reliable Reset All action.
5. Added filter-specific no-results recovery.
6. Unified Dashboard and Transaction History filter state and list actions.
7. Added migration-managed indexes for larger transaction histories.
8. Tested wildcard searches, same-day ranges, blank notes, renamed records, combined filters, reset behavior, and large histories.

### Deliverables

- Searchable transaction history.
- Combined advanced filters.
- Active-filter display and Reset All action.
- Filter-specific empty state.
- Database indexes and automated filter tests.

### Completion gate

**Passed.** Every filter works alone and in combination, Reset All restores the
full list, no-results states provide clear recovery, and stable newest-first
queries use migration-managed indexes on a tested 10,000-record history.

---

## Phase 9 — Beta Testing and Version 1.0 Readiness

**Status:** Completed in `v1.0.0`
**Priority:** Final release gate

### Objective

Prove with repeatable evidence that Enkryon's complete core product is stable, recoverable, usable, and safe enough to become version 1.0.

### Work plan

1. Run a full clean-install and first-time-user regression test.
2. Run upgrade tests from every supported alpha and beta database version.
3. Verify migrations, backup, restore, Clear All Data, reinstall, and persistence behavior.
4. Test startup, totals, filtering, scrolling, and saving with large datasets.
5. Complete accessibility, font-size, and supported-device tests.
6. Resolve all critical and high-severity defects and document accepted lower-severity limits.
7. Make the README, screenshots, version values, database documentation, architecture documentation, changelog, and release notes match the shipped app.
8. Add a real license file or clearly revise the repository's usage terms.
9. Build, sign, install, upgrade, and verify the version 1.0 release candidate.

### Deliverables

- Complete regression report.
- Upgrade, backup, and recovery evidence.
- Performance and device-matrix results.
- Accurate user and developer documentation.
- Signed version 1.0 release candidate APK or AAB.

### Version 1.0 gate

Enkryon may become version 1.0 only when:

- Financial calculations remain exact in centavos.
- Every supported older database upgrades without data loss.
- Backup and restore pass round-trip testing.
- GitHub Actions and the complete test suite pass.
- Android clean-install and official-to-official upgrade tests pass.
- No unresolved critical or high-severity defects remain.
- Accessibility and responsive-layout tests pass.
- Documentation, version values, and the released artifact agree.

**Passed.** Version 1.0 established the official stable baseline used by the
version 1.x feature updates below.

---

## Phase 10 — Version 1.x Feature Expansion

**Status:** In progress — Update 3 contract baseline

### Objective

Add major financial capabilities without weakening the accurate, upgrade-safe, recoverable core established in Phases 1–9.

### Candidate order after version 1.0

1. Account transfers (`v1.1.0`) — released.
2. Pending Transactions (`v1.2.0`) — released.
3. Pass-through Transfers (`v1.3.0`) — the originally requested cash-out or money-forwarding workflow.
4. Daily Bank Interest (`v1.4.0`) — planned after transfer semantics are stable.
5. Statistical Visualizations (`v1.5.0`) — planned after pending, pass-through, and interest records are defined.
6. Budget tracking, recurring transactions, CSV import/export, dark mode, and optional synchronization.

### Update 1 — Account Transfers (`v1.1.0`)

The implementation adds one atomic transfer record with exact centavos,
direction-aware per-account balances, all-account net-zero behavior, unified
activity history, edit/delete/undo, account-deletion protection, migration 5,
backup format 2, and format-1 restore compatibility.

The release completed with the complete suite, GitHub Actions, signed Android
artifact checks, clean installation, and transfer/recovery verification. The
official physical-device v1.0.0-to-v1.1.0 in-place upgrade was waived by the
release owner and remains an explicit carried exception.

### Update 2 — Pending Transactions (`v1.2.0`)

Pending Transactions add an explicit internal `temporary` or `posted` status to
the existing transaction identity. Pending records remain visible and searchable
in Activity History but are fully non-posting until the user converts them
atomically. They cannot affect account balances, Income, Expenses, category
totals, net cash flow, or statistical financial aggregates.

Migration 6 extends the existing `transactions` table with constrained
posting status and a query-plan-verified status-history index. Dashboard and
Activity History now expose an explicit Pending filter, while Income and
Expense filters return posted records only. Backup format 3 preserves exact
posting status, while format-1 and format-2 transactions normalize to posted
before restore. The seven
weighted tasks are contract and baseline (7%), persistence
(18%), workflows (18%), interface (20%), totals and activity integration (16%),
backup and recovery (11%), and release closeout (10%). The locked rules are in
`docs/development/temporary-transactions.md`.

### Update 3 — Pass-through Transfers (`v1.3.0`)

Pass-through Transfers cover cases such as a friend sending money into the
user's Bank account while the user gives the same principal from Cash. The
canonical ledger direction is `Cash → Bank`: source decreases, destination
increases, and the all-account balance remains unchanged. The principal never
changes Income, Expenses, category totals, or posted net cash flow.

Task 1 locks migration 7 to extend the existing `account_transfers` ledger with
`internal` and `pass_through` kinds. Existing transfers normalize to `internal`.
Pass-through records add an optional counterparty; purpose/details stay in Notes,
and any real service fee is recorded separately as a posted Expense. The primary
Transfer filter includes both kinds while Advanced Filters distinguish Internal
from Pass-through. Backup format 4 will preserve the new kind and counterparty
while older supported backups normalize transfers to Internal. The locked rules
are in `docs/development/pass-through-transfers.md`.

### Update 4 — Daily Bank Interest (`v1.4.0`)

Daily bank interest will provide deterministic, float-free estimated accruals
for configured accounts. Estimates remain non-posting; only explicit
reconciliation creates a normal posted Income transaction.

### Update 5 — Statistical Visualizations (`v1.5.0`)

Statistics will add exact posted income, expense, and net summaries,
time-bucket comparisons, expense breakdowns, and textual equivalents.
Transfers, pending records, pass-through transfers, and estimated interest
remain separate context and must not enter posted financial metrics.

Each major feature requires its own objective, user flow, data design, database
migration, automated tests, Android regression test, and release notes before
implementation begins.

## Immediate Action Order

The next work should be completed in this order:

1. Completed: lock the fully non-posting Pending Transaction contract and
   record the clean v1.1.0 baseline.
2. Completed: add migration 6 and status-aware persistence without changing
   migrations 1 through 5.
3. Completed: add pending form state and UI-independent save, edit, atomic
   post, delete, and restore workflows.
4. Completed: add explicit pending form actions, non-color-only activity-card
   treatment, and guarded direct posting from Dashboard and Activity History.
5. Completed: add posted-only Income and Expense filters, an explicit
   Pending filter, refresh invariants, mixed-history combinations, and
   10,000-record integration while excluding pending records from every
   posted financial calculation.
6. Completed: add backup format 3, exact status round trips, format-1/2
   normalization, malformed-status rejection, sequences, integrity, Clear All
   Data, relaunch, and rollback evidence.
7. In progress: the v1.2.0 source identity, changelog, release notes, architecture,
   database guide, checklist, and desktop regression evidence are prepared.
   GitHub Actions, the signed Android artifact, clean installation, official
   v1.1.0 upgrade, and final artifact evidence remain.

Pending Transaction posting semantics are released and verified. Begin
Pass-through Transfers with Task 1 only; do not begin Daily Bank Interest or
Statistical Visualizations until the Pass-through contract and release are
complete.

## Rule for Completing Every Phase

At the end of each phase:

1. Run the complete automated test suite.
2. Perform the Android checks relevant to the phase.
3. Update user and developer documentation.
4. Record unresolved defects and assign each one to a later phase.
5. Verify every item in the phase completion gate.
6. Record the evidence in a short phase-completion report.

This keeps the roadmap based on proven results and prevents unfinished work from being hidden by new features.
