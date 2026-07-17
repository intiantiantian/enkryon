# Enkryon Development Roadmap

Updated: July 17, 2026
Current release: `v0.4.0`
Current position: Phase 2 is complete; Phase 3 is next

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

| Area | Current state in `v0.4.0` | What it means for the roadmap |
|---|---|---|
| Core product | Accounts, category groups, categories, income and expense transactions, editing, deletion, dashboard totals, transaction-type filters, and local storage are implemented. | Improve reliability and usability before adding major features. |
| Financial accuracy | Transaction amounts are stored and calculated as integer centavos instead of decimal `REAL`/Python `float` values. | The main money-rounding risk identified in the old roadmap has been resolved. |
| Database upgrades | A `schema_migrations` table and three ordered, transactional migrations are present. They create the schema, convert old amounts to centavos, and add validation rules. | Future database changes can build on the migration framework instead of replacing user data. |
| Data rules | The database rejects invalid amounts, dates, transaction types, blank names, untrimmed names, and several duplicate-name cases. Foreign keys remain enabled. | Important data rules are enforced even if a screen-level check is missed. |
| Automated tests | The Phase 2 verification report records `88 passed`. Tests cover repositories, migrations, exact money conversion, validation, payloads, versioning, theme tokens, and reusable widgets. | The local test foundation is strong enough to place into continuous integration. |
| Versioning | `main.py` defines `0.4.0`; Buildozer reads that value; the README uses the matching APK filename. | Version disagreement has been resolved. |
| Android release | The signed `Enkryon-v0.4.0.apk` was aligned, signature-verified, clean-installed, and smoke-tested with a centavo transaction. | Several Phase 4 tasks were completed early, but repeatable release automation and upgrade testing still remain. |
| Android packaging | Tests, documentation, caches, local environments, build folders, and local database files are excluded from packaging. The build targets ARM64 and ARMv7 and produces an APK. | Packaging cleanup has started; configuration and release documentation still need hardening. |
| Automated checks on GitHub | No GitHub Actions workflow is present in the ZIP. | Phase 3 is the next priority. |
| Architecture | Repositories, services, screens, utilities, widgets, and theme modules exist. Screens still contain substantial workflow logic, especially the add-transaction screen. | Continue architecture cleanup after automatic quality checks are established. |
| Backup and recovery | The app can clear all data, but it has no user-controlled backup and restore flow. | Recovery must be added before Enkryon leaves alpha. |
| Search and advanced filters | Transaction-type filtering exists. Search, date range, account, category, and combined filters are not yet complete. | Complete these in Phase 8 rather than mixing them into reliability work. |

## Phase Overview

| Phase | Plain-language objective | Status |
|---|---|---|
| 1. Safe Foundation and Consistent Design | Make the existing app safer, easier to maintain, and visually consistent. | Completed |
| 2. Exact Money and Safe Database Upgrades | Prevent rounding errors and upgrade existing databases without losing data. | Completed |
| 3. Automatic Quality Checks | Test every change automatically so defects are caught before release. | Next |
| 4. Reliable Android Releases | Make Android builds repeatable, correctly signed, clearly versioned, and safe to install as upgrades. | Partially completed |
| 5. Simpler, More Maintainable Code | Move business rules out of large screens and give each code layer one clear job. | Planned |
| 6. Clear, Accessible, Responsive User Experience | Make all existing workflows comfortable and understandable across supported phones. | Planned |
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

### Documentation follow-up

The old Phase 1.2 summary still says money uses `REAL`, migrations do not exist, and account duplicates are not case-insensitive. Those statements were true when that summary was written but were resolved in Phase 2. Update the summary so historical documents do not look like current defects.

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

### Documentation follow-up

- Expand `docs/development/database.md` to explain the migration system, integer-centavo storage, and database rules—not only the database location.
- Correct the unfinished code fence in `docs/audits/phase-2-verification.md`.
- Update the stale Phase 1.2 “known remaining issues” list.

These are documentation cleanups. They do not reopen the verified Phase 2 implementation.

### Completion gate

**Passed.** Financial values use exact centavos, old data has a tested upgrade path, failed migrations are recoverable, repeat runs are safe, database rules are enforced, and release version values agree.

---

## Phase 3 — Automatic Quality Checks

**Status:** Next
**Priority:** High

### Objective

Run the same dependable checks for every proposed change so a broken migration, calculation, or core workflow is discovered before it becomes a release.

### Work plan

#### 3.1 Reproducible test setup

1. Create a development dependency file separate from the Android runtime dependencies.
2. Include the exact testing and quality-tool versions needed by contributors and GitHub Actions.
3. Document the setup and the commands for tests, syntax checks, and other required checks.

#### 3.2 GitHub Actions

1. Add a workflow that runs on pushes and pull requests.
2. Install the documented development environment.
3. Run Python compilation checks.
4. Run the complete automated test suite.
5. Make a failed required check block release preparation.

#### 3.3 Stronger correctness tests

1. Add upgrade tests using saved database files from supported older versions, not only newly created in-memory examples.
2. Add service tests for creating, editing, deleting, validating, and handling failed transactions.
3. Test missing records, duplicate names, invalid dates, invalid amounts, database failures, and migration incompatibilities.
4. Add headless screen or app-start smoke tests where Kivy can run them reliably.
5. Produce an initial coverage report and focus improvements on migrations, financial calculations, repositories, and services.

#### 3.4 Documentation cleanup

1. Correct the stale Phase 1.2 issue list.
2. Expand the database documentation for Phase 2.
3. Repair the Phase 2 verification report formatting.
4. Link the full roadmap from the README.

### Deliverables

- Reproducible development/test dependency setup.
- GitHub Actions workflow for pushes and pull requests.
- Automatic compilation and test results.
- Old-version database fixtures and upgrade tests.
- Service and failure-path tests.
- Clear local testing instructions.
- Corrected Phase 1 and Phase 2 documentation.

### Completion gate

Phase 3 is complete when a fresh local environment and GitHub Actions run the same required checks, every pull request receives an automatic pass/fail result, older database fixtures upgrade successfully, and a failed financial or migration test prevents release preparation.

---

## Phase 4 — Reliable Android Releases

**Status:** Partially completed
**Priority:** High

### Objective

Produce Android releases that are repeatable, correctly signed, appropriately packaged, clearly documented, and safe to install over the previous official release.

### Already completed

- Excluded tests, documentation, caches, virtual environments, build folders, and local databases from packaging.
- Set `main.py` as the version source used by Buildozer.
- Configured portrait orientation, ARM64 and ARMv7 architectures, and APK output.
- Built `Enkryon-v0.4.0.apk`.
- Signed `v0.4.0` with the permanent Enkryon release certificate.
- Verified the APK signature and alignment.
- Recorded package, version, architecture, size, checksum, and certificate information.
- Passed a clean-install Android smoke test.

### Remaining work

1. Explicitly set supported Android API and minimum API values in `buildozer.spec` instead of leaving them as commented defaults.
2. Document separate debug and release build commands.
3. Document the signing process while keeping passwords and private keys outside the repository.
4. Add an Android adaptive icon and optimize oversized launcher/splash assets where possible.
5. Review the approximately 51 MB APK and remove avoidable size without risking runtime reliability.
6. Standardize artifact naming, checksums, changelog entries, and release-note format.
7. Create one release checklist covering build, signature, alignment, install, launch, migrations, persistence, backup, core workflows, and version display.
8. Build the next test release with the same permanent certificate and test an in-place upgrade from `v0.4.0`.
9. Confirm that user records and schema migrations survive the official-to-official upgrade.
10. Decide and document the intended Android auto-backup behavior so it agrees with Enkryon's privacy and recovery design.

### Deliverables

- Explicit and reviewed Android build settings.
- Debug and release build instructions.
- Secure signing instructions.
- Optimized/adaptive application icon assets.
- Standard artifact, checksum, changelog, and release-note process.
- Android release checklist.
- Successful in-place upgrade evidence from `v0.4.0`.

### Completion gate

Phase 4 is complete when another developer can reproduce the documented build, the artifact contains no development-only files, the signature and alignment pass, and the new official APK installs over `v0.4.0` without losing user data.

---

## Phase 5 — Simpler, More Maintainable Code

**Status:** Planned
**Priority:** Medium-high

### Objective

Make changes safer by moving business rules out of large screen files and giving screens, services, repositories, utilities, and widgets one clear responsibility each.

### Work plan

1. Split `screens/add_transaction.py` into smaller form-state, selection, date/time, and save/update responsibilities.
2. Move transaction creation, editing, deletion, and validation workflows into services.
3. Keep screens focused on navigation, reading user input, showing results, and rendering state.
4. Standardize repository results and errors so the app can distinguish duplicates, referenced records, missing records, validation failures, and database failures.
5. Replace `print()` and unclear Boolean failure results with explicit, testable error handling.
6. Use context-managed database connections and consistent transaction handling.
7. Introduce small named or typed records so screen code does not rely on tuple positions.
8. Remove repeated dialog, deletion, filtering, refresh, and navigation logic.
9. Continue replacing repeated visual structures with shared widgets and design values.
10. Protect every refactor with behavior-preserving tests.

### Deliverables

- Smaller screen controllers.
- Complete service boundaries for transaction workflows.
- Consistent repository results and errors.
- Named data objects between the database and interface layers.
- Updated architecture documentation and tests.

### Completion gate

Phase 5 is complete when screens contain no raw persistence or financial rules, core workflows can be tested without rendering the interface, failures have clear meanings, and repeated behaviors have one maintained implementation.

---

## Phase 6 — Clear, Accessible, Responsive User Experience

**Status:** Planned
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

1. Create a separate, reproducible development/test dependency setup.
2. Add GitHub Actions for compilation and the complete test suite.
3. Add real old-version database fixtures and upgrade tests.
4. Add service and failure-path tests.
5. Correct stale Phase 1 and Phase 2 documentation.
6. Explicitly pin Android API settings and document debug/release builds.
7. Test the next official APK as an in-place upgrade from `v0.4.0`.
8. Resume architecture simplification only after the automatic checks protect existing behavior.

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
