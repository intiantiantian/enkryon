# Enkryon Development Roadmap

Updated: July 20, 2026
Current release: `v0.4.8`
Current position: Phase 5 is complete; Phase 6 is next

## Purpose

This roadmap guides Enkryon from its current working Android release to a dependable version 1.0 personal finance tracker.

The phases are ordered by risk. Enkryon must first protect financial data, calculate money exactly, catch defects automatically, and survive app upgrades. Only after that foundation is dependable should the project add major features such as reports, budgets, recurring transactions, or cloud synchronization.

## Status Guide

| Status | Meaning |
|---|---|
| Completed | The objective was implemented and verified. |
| Next | This is the immediate development priority. |
| Partially completed | Some work is already proven, but the phase still has required items. |
| Planned | The phase has not started in a focused way. |
| Deferred | Do not begin this work until the version 1.0 foundation is ready. |

## Current Project Snapshot

| Area | Current state in `v0.4.8` | What it means for the roadmap |
|---|---|---|
| Core product | Accounts, category groups, categories, income and expense transactions, editing, deletion, dashboard totals, transaction-type filters, and local storage are implemented. | Improve reliability and usability before adding major features. |
| Financial accuracy | Transaction amounts are stored and calculated as integer centavos instead of decimal `REAL`/Python `float` values. | The main money-rounding risk identified in the old roadmap has been resolved. |
| Database upgrades | A `schema_migrations` table and three ordered, transactional migrations are present. They create the schema, convert old amounts to centavos, and add validation rules. | Future database changes can build on the migration framework instead of replacing user data. |
| Data rules | The database rejects invalid amounts, dates, transaction types, blank names, untrimmed names, and several duplicate-name cases. Foreign keys remain enabled. | Important data rules are enforced even if a screen-level check is missed. |
| Automated tests | The suite contains `252` passing tests covering migrations, repositories, managed connections, named records, form state, workflow services, shared screen actions, and Android release configuration. | Keep increasing coverage where behavior and risk justify it rather than chasing an arbitrary percentage. |
| Versioning | `main.py` defines `0.4.8`; Buildozer, artifact names, checksums, and release records use the same value. | The roadmap version and Android artifact now agree. |
| Android release | The permanently signed `Enkryon-v0.4.8.apk` passed checksum, signature, alignment, packaging, clean-launch, and in-place upgrade checks from official `v0.4.0`. | Phase 4's Android release gate is complete. |
| Android packaging | Development files and duplicated source assets are excluded. The verified APK targets API 36, supports API 24 and later, contains ARM64 and ARMv7, and disables Android auto-backup. | Packaging and privacy behavior are explicit and test-protected. |
| Automated checks on GitHub | GitHub Actions installs the pinned development environment, compiles the source, and runs all tests with coverage on pushes, pull requests, and manual runs. | Broken correctness checks are visible before release preparation. |
| Architecture | Named records cross repository boundaries, managed connections protect database work, services own account/category/transaction workflows, transaction form state is explicit, and shared screen helpers own repeated result and list actions. | Phase 6 can improve the interface without moving financial or persistence rules back into screens. |
| Backup and recovery | The app can clear all data, but it has no user-controlled backup and restore flow. | Recovery must be added before Enkryon leaves alpha. |
| Search and advanced filters | Transaction-type filtering exists. Search, date range, account, category, and combined filters are not yet complete. | Complete these in Phase 8 rather than mixing them into reliability work. |

## Phase Overview

| Phase | Plain-language objective | Status |
|---|---|---|
| 1. Safe Foundation and Consistent Design | Make the existing app safer, easier to maintain, and visually consistent. | Completed |
| 2. Exact Money and Safe Database Upgrades | Prevent rounding errors and upgrade existing databases without losing data. | Completed |
| 3. Automatic Quality Checks | Test every change automatically so defects are caught before release. | Completed |
| 4. Reliable Android Releases | Make Android builds repeatable, correctly signed, clearly versioned, and safe to install as upgrades. | Completed |
| 5. Simpler, More Maintainable Code | Move business rules out of large screens and give each code layer one clear job. | Completed |
| 6. Clear, Accessible, Responsive User Experience | Make all existing workflows comfortable and understandable across supported phones. | Next |
| 7. Backup, Restore, and Recovery | Let users preserve and recover their local financial records safely. | Planned |
| 8. Transaction Search and Advanced Filters | Help users find specific transactions quickly, even in large histories. | Planned |
| 9. Beta Testing and Version 1.0 Readiness | Prove that the complete core app is stable enough for a version 1.0 release. | Planned |
| 10. Major Feature Expansion | Add reports, budgets, recurring transactions, and other large features after the core is dependable. | Deferred |

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

## Phase 6 — Clear, Accessible, Responsive User Experience

**Status:** Next
**Priority:** Medium-high

### Objective

Make every existing workflow understandable and comfortable on supported Android phones, including small screens, large text, long names, empty data, and error situations.

### Work plan

1. Test first-use, populated, empty, error, and destructive states for every screen.
2. Preserve an unfinished transaction form when users temporarily open Accounts or Categories.
3. Improve dashboard information hierarchy and reduce low-value empty or decorative space.
4. Improve transaction-row alignment, spacing, amount emphasis, and action placement.
5. Test backgrounds, scrolling, fixed controls, system safe areas, and Android back behavior.
6. Test small and large phones, long names and notes, large amounts, narrow screens, and system font scaling.
7. Enforce comfortable touch targets, readable contrast, clear selected states, and consistent destructive actions.
8. Distinguish income and expenses using words and visual styling, not color alone.
9. Add useful next-step actions to empty states.
10. Add About, version, local-data, and privacy information to Settings.
11. Complete the visual transition of dropdowns, dialogs, menus, selection panels, confirmation prompts, and other overlay-style interface elements into Enkryon’s customized `MDCard`-based components so they share the same spacing, shape, elevation, typography, selected states, and emerald-and-gold visual language as the rest of the application.
12. Replace repository screenshots only after the layouts and customized interface components pass the supported-device tests.

### Deliverables

- Screen-by-screen user-experience checklist.
- Supported-device and font-size test matrix.
- Accessibility and contrast audit.
- Improved transaction cards, navigation states, and empty states.
- Customized `MDCard`-based dropdowns, dialogs, menus, selection panels, and confirmation prompts.
- Updated Settings information and repository screenshots.

### Completion gate

Phase 6 is complete when core workflows have no clipping or inaccessible controls across the supported device matrix, navigation preserves expected state, mistakes are recoverable, and important information remains readable with long or large content.

---

## Phase 7 — Backup, Restore, and Recovery

**Status:** Planned
**Priority:** High before leaving alpha

### Objective

Give users a safe, understandable way to preserve and recover their local financial records before clearing data, changing devices, or installing risky upgrades.

### Work plan

1. Define a versioned backup format containing the database version, app version, export date, and record counts.
2. Export accounts, category groups, categories, and transactions without changing relationships or centavo values.
3. Validate an entire backup before changing the current database.
4. Restore inside a database transaction and roll back if any step fails.
5. Show what will be restored and require confirmation before replacing current data.
6. Offer a backup before Clear All Data and before any future high-risk migration where practical.
7. Handle malformed, incomplete, incompatible, and partially corrupted backup files safely.
8. Explain where Enkryon stores data and backups and how users can transfer them.
9. Test empty, normal, large, corrupted, and old-version backup round trips.

### Deliverables

- Local backup/export flow.
- Validated restore/import flow.
- Corruption and incompatibility handling.
- Round-trip and failure-path tests.
- User-facing recovery instructions.

### Completion gate

Phase 7 is complete when a populated database can be exported, removed, restored, and verified without changing balances, relationships, dates, notes, names, or transaction IDs.

Cloud synchronization is not part of this phase.

---

## Phase 8 — Transaction Search and Advanced Filters

**Status:** Planned
**Priority:** Medium

### Objective

Help users quickly find a specific transaction by its text, account, category, type, or date—even when the history becomes large.

### Work plan

1. Add search across notes, account names, category-group names, and category names.
2. Add filters for account, category group, category, and date range.
3. Make search, transaction type, account, category, and date filters work together.
4. Show active filters and provide a reliable Reset All action.
5. Show a specific no-results state when filters match nothing.
6. Keep filter behavior consistent between Dashboard recent transactions and the full history screen.
7. Add database indexes needed for larger histories.
8. Test same-day date ranges, blank notes, renamed records, combined filters, no results, and reset behavior.

### Deliverables

- Searchable transaction history.
- Combined advanced filters.
- Active-filter display and Reset All action.
- Filter-specific empty state.
- Database indexes and automated filter tests.

### Completion gate

Phase 8 is complete when every filter works alone and in combination, Reset All always restores the full list, no-results states are clear, and larger histories remain responsive.

---

## Phase 9 — Beta Testing and Version 1.0 Readiness

**Status:** Planned
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

---

## Phase 10 — Major Feature Expansion

**Status:** Deferred until the version 1.0 gate passes

### Objective

Add major financial capabilities without weakening the accurate, upgrade-safe, recoverable core established in Phases 1–9.

### Candidate order after version 1.0

1. Reports and charts.
2. Budget tracking.
3. Recurring transactions.
4. Broader import/export formats such as CSV.
5. Dark mode.
6. Optional cloud synchronization.

Each major feature should have its own objective, user flow, data design, database migration, automated tests, Android regression test, and release notes before implementation begins.

## Immediate Action Order

The next work should be completed in this order:

1. Begin Phase 6 with a screen-by-screen experience checklist and a supported-device and font-size test matrix.
2. Preserve unfinished transaction-form state when users temporarily manage accounts or categories.
3. Test navigation, scrolling, safe areas, touch targets, contrast, long content, and destructive actions across the supported matrix.
4. Complete the customized card-based overlays and improve transaction rows, empty states, and Settings information.
5. Replace repository screenshots only after the supported-device checks pass.

Do not begin reports, budgets, recurring transactions, dark mode, or cloud synchronization while the version 1.0 foundation remains incomplete.

## Rule for Completing Every Phase

At the end of each phase:

1. Run the complete automated test suite.
2. Perform the Android checks relevant to the phase.
3. Update user and developer documentation.
4. Record unresolved defects and assign each one to a later phase.
5. Verify every item in the phase completion gate.
6. Record the evidence in a short phase-completion report.

This keeps the roadmap based on proven results and prevents unfinished work from being hidden by new features.
