# Changelog

All notable Enkryon changes are recorded here. Entries describe changes
that affect users, stored data, compatibility, privacy, or releases.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Before version 1.0, Enkryon uses `major.phase.subphase` as its roadmap
version reference.

## [Unreleased]

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
