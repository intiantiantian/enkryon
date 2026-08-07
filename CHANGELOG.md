# Changelog

All notable Enkryon changes are recorded here. Entries describe changes
that affect users, stored data, compatibility, privacy, or releases.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Before version 1.0, Enkryon uses `major.phase.subphase` as its roadmap
version reference.

## [Unreleased]

## [1.3.0] - 2026-08-07

### Added

- Pass-through Transfers for completed cash-out or money-forwarding exchanges,
  stored as linked account outflow/inflow effects rather than Income or Expense.
- Optional counterparty metadata plus dedicated Internal and Pass-through
  Advanced Filters and searchable activity semantics.
- Database migration 7 with constrained `internal` and `pass_through` transfer
  kinds.
- Backup format 4 with exact transfer-kind and counterparty preservation.

### Changed

- General Transfer filtering now includes both Internal and Pass-through records.
- Pass-through activity presents explicit linked effects such as
  `Cash outflow | Bank inflow` so it is not mistaken for movement of the same
  physical money between the user's accounts.
- Application and Android release identity use version `1.3.0`.

### Fixed

- Pass-through edit, delete, undo, restore, and backup workflows preserve both
  account effects atomically and cannot change Income, Expenses, category totals,
  or the all-account balance.
- User-facing transfer copy avoids decorative direction glyphs where plain text
  is more portable.

## [1.2.0] - 2026-08-06

### Added

- Pending Transactions for planned or provisional income and expense records
  that remain visible without affecting balances or posted totals.
- Explicit Save as Pending and Post Transaction actions, Pending status text,
  direct posting from activity cards, and a dedicated Pending activity filter.
- Database migration 6 with constrained posting status and an indexed
  newest-first Pending-history access path.
- Backup format 3 with exact posted/Pending status preservation.

### Changed

- Income and Expense activity filters now return posted records only, while All
  includes posted transactions, Pending transactions, and account transfers.
- Format-1 and format-2 backup transactions normalize to posted before restore.
- Application, Android artifact, release documentation, and roadmap candidate
  identity now use version `1.2.0`.

### Fixed

- Failed or repeated posting cannot apply a transaction to balances or totals
  more than once.
- Pending delete, undo, export, Clear All Data, restore, and relaunch workflows
  preserve non-posting financial semantics.

## [1.1.0] - 2026-08-04

### Added

- First-class account transfers with distinct source and destination
  accounts, exact integer-centavo amounts, date/time, and optional notes.
- Transfer creation, editing, deletion, undo restoration, and account-safety
  rules that protect referenced accounts.
- Unified Dashboard and Activity History entries for income, expenses, and
  transfers, including transfer search and account/date/type filters.
- Database migration 5 with transfer constraints and indexed newest-first,
  outgoing, and incoming activity access paths.
- Backup format 2 with transfer export, validation, replacement restore,
  record-count, sequence, integrity, and rollback support.

### Changed

- Per-account balances now subtract outgoing transfers and add incoming
  transfers; the combined balance, Income, and Expenses remain unchanged.
- Dashboard actions use a responsive two-by-two arrangement for Add
  Transaction, Transfer Funds, Manage Accounts, and Manage Categories.
- Compatible v1.0 backup documents remain restorable and are interpreted as
  containing no transfers.
- Application, Android artifact, release documentation, and roadmap identity
  now use version `1.1.0`.

### Fixed

- Transfer direction labels use rendering-safe text instead of an unsupported
  arrow glyph.
- Transfer-aware clear and restore failures roll back without leaving partial
  records.

## [1.0.0] - 2026-07-28

### Added

- Proprietary source-code terms that allow viewing and portfolio evaluation
  while reserving copying, modification, distribution, and reuse rights.
- Release-readiness evidence covering clean installation, legacy database
  upgrades, backup and recovery, financial integrity, responsive layouts,
  enlarged fonts, and accessibility.

### Changed

- Transaction History now virtualizes card rendering so 10,000-record
  histories remain responsive without creating every complete card at once.
- Application, Android package, release documentation, and roadmap identity
  now use version `1.0.0`.

### Fixed

- Large Transaction History datasets no longer exhaust device memory during
  initial screen loading.
- Recycled transaction cards keep stable row heights on first entry, after
  delayed content measurement, while scrolling, and after filtering.

## [0.8.0] - 2026-07-26

### Added

- Transaction search across notes, account names, category-group names, and
  category names.
- Combined account, transaction-type, category-group, category, and inclusive
  date-range filters.
- Active-filter summaries, Reset All behavior, and filter-specific no-results
  recovery.
- Migration-managed transaction-history indexes and a 10,000-record query-plan
  regression test.

### Changed

- Transaction History now uses stable newest-first ordering by date and
  transaction ID.
- Dashboard recent transactions and the full history use shared transaction
  filter state and list actions.
- New backup exports record database version 4, while compatible version 3
  backups remain restorable.

### Fixed

- Search wildcard characters are treated literally instead of changing the
  intended search pattern.
- Same-day date ranges include the complete selected day.
- Blank transaction notes remain safe during combined searches.

## [0.7.0] - 2026-07-25

### Added

- Versioned JSON backup export containing application, database,
  export-date, record-count, and financial-record data.
- Complete backup validation before current application data can change.
- Restore preview showing backup metadata and record counts.
- Android system document-picker support for backup export and import.
- A two-stage Clear All Data flow that offers backup before deletion.
- Automated round-trip, corruption, incompatibility, rollback,
  document-transfer, and Settings workflow tests.

### Changed

- Restore now deliberately replaces current application data inside one
  database transaction after explicit confirmation.
- Settings now explains local storage, backup, restore, and destructive-data
  behavior.
- Backup and restore use user-selected documents without requesting broad
  Android storage permission.

### Fixed

- Failed restore operations roll back instead of leaving partially replaced
  data.
- Cancelled or failed backup-before-clear operations never advance to data
  deletion.
- Android document-picker results return through Kivy's UI thread so restore
  previews and post-export confirmations appear correctly.

## [0.6.0] - 2026-07-23

### Added

- Reusable card-based selection, input, and confirmation overlays with
  consistent spacing, selected states, and destructive-action treatment.
- Actionable empty states and Settings information covering the application
  version, local data, and privacy.
- Responsive-layout, accessibility, long-content, form-preservation, and
  overlay-behavior regression tests.
- Named account, category-group, category, and transaction records between
  repositories and interface code.
- Explicit transaction form state with tested dependent-selection
  transitions.
- Account and category workflow services with clear, testable action
  results.
- Behavior-preserving tests for screen workflows, managed connections,
  repository failures, form state, and shared interface actions.

### Changed

- Dashboard, transaction cards, navigation, scrolling, and fixed controls
  now adapt more reliably to narrow screens and enlarged text.
- Unfinished transaction form values survive temporary navigation to account
  and category management.
- Income and expense transactions use explicit text and visual treatment
  instead of relying only on color.
- Selection, input, and confirmation workflows now use Enkryon's shared
  customized overlay components.
- Transaction creation, editing, deletion, validation, and view preparation
  now run through transaction services.
- Database reads and writes use managed connections with consistent commit,
  rollback, cleanup, and foreign-key behavior.
- Repository write outcomes distinguish validation, duplicate, referenced,
  missing-record, and database failures.
- Dashboard and Transaction History share filtering, edit navigation,
  deletion, confirmation-dialog, and refresh behavior.
- Account, category, and transaction screens share action-result rendering
  instead of repeating snackbar and refresh sequencing.

### Fixed

- Android Back and desktop Escape dismiss the active overlay before allowing
  underlying screen navigation.
- The Dashboard current balance remains fully readable through
  `₱9,999,999.00` and switches to compact formatting from `₱10,000,000`.
- Floating input labels remain clear of field boundaries in blank and
  prefilled dialogs.
- Failed transaction inserts, updates, and deletions no longer appear
  successful to calling services.
- Settings reports a clear-data success message only after the repository
  confirms that data was cleared.

## [0.4.8] - 2026-07-19

### Added

- Adaptive Android launcher icon resources.
- Repeatable Android build, signing, verification, and checksum procedures.
- Automated Android configuration and packaging checks.
- A standardized Android release checklist and release-record format.

### Changed

- Android builds now pin their compatibility and toolchain versions.
- Release APKs exclude repository screenshots and duplicated source assets.
- Android automatic backup is explicitly disabled pending Enkryon's
  user-controlled backup and restore feature.
- The release version advanced to `0.4.8` for Phase 4 subphase 8.
- The permanently signed APK was verified as an in-place upgrade from
  official `v0.4.0` without losing the controlled financial dataset.

## [0.4.0] - 2026-07-17

### Added

- Ordered, transactional, and repeatable database migrations.
- Database validation for names, dates, transaction types, relationships,
  and positive transaction amounts.
- Automated regression tests for migrations and financial calculations.

### Changed

- Transaction amounts are stored as exact integer centavos.
- Application and Android package versions use the same `0.4.0` value.

### Fixed

- Financial calculations no longer depend on binary floating-point values.
- Legacy transaction data upgrades without losing IDs, relationships, or
  totals.
