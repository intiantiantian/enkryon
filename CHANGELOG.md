# Changelog

All notable Enkryon changes are recorded here. Entries describe changes
that affect users, stored data, compatibility, privacy, or releases.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Before version 1.0, Enkryon uses `major.phase.subphase` as its roadmap
version reference.

## [Unreleased]

### Added

- Named account, category-group, category, and transaction records between
  repositories and interface code.
- Explicit transaction form state with tested dependent-selection
  transitions.
- Account and category workflow services with clear, testable action
  results.
- Behavior-preserving tests for screen workflows, managed connections,
  repository failures, form state, and shared interface actions.

### Changed

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
