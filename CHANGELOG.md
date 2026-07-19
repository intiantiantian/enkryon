# Changelog

All notable Enkryon changes are recorded here. Entries describe changes
that affect users, stored data, compatibility, privacy, or releases.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and Enkryon uses semantic `MAJOR.MINOR.PATCH` versions.

## [Unreleased]

### Added

- Adaptive Android launcher icon resources.
- Repeatable Android build, signing, verification, and checksum procedures.
- Automated Android configuration and packaging checks.

### Changed

- Android builds now pin their compatibility and toolchain versions.
- Release APKs exclude repository screenshots and duplicated source assets.
- Android automatic backup is explicitly disabled pending Enkryon's
  user-controlled backup and restore feature.

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
