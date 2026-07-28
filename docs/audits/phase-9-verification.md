# Phase 9 Verification

## Status

In progress. The Phase 9 baseline was established on July 27, 2026.

## Automated Baseline

- Python `3.13.14` was used.
- Dependency validation reported no broken requirements.
- Python source compilation completed without errors.
- All `499` automated tests passed.
- Total branch coverage measured `81%`.
- The application version remained `0.8.0`.
- Buildozer continued to derive the version from `main.py`.
- Git whitespace validation completed without errors.
- The `phase-9-v1-readiness` working tree was clean.

## Beta-Test Profiles

- **Clean profile:** no existing Enkryon installation or application data.
- **Upgrade profile:** official `v0.8.0` containing the controlled demo dataset.
- **Recovery profile:** populated data with a verified backup exported before destructive checks.
- **Scale profile:** at least 10,000 transactions covering search and filter combinations.
- **Display profiles:** supported narrow and larger phone layouts at default and enlarged font sizes.

## Verification Matrix

| ID | Check | Required result | Checkpoint | Status |
|---|---|---|---:|---|
| P9-01 | Clean installation and first launch | App starts without errors and every empty state provides the correct next action. | 2 | Passed |
| P9-02 | Legacy database migrations | Every retained supported database fixture upgrades without changing IDs, relationships, exact centavo values, or totals. | 3 | Passed |
| P9-03 | Official `v0.8.0` upgrade | The signed release candidate installs over `v0.8.0` and preserves all controlled data. | 5 | Pending |
| P9-04 | Core workflows and persistence | Account, category, and transaction creation, editing, deletion, filtering, and relaunch persistence pass. | 4 | Passed |
| P9-05 | Backup round trip | Export, preview, replacement restore, IDs, relationships, notes, dates, and totals remain correct. | 4 | Passed |
| P9-06 | Restore failure protection | Invalid, incompatible, corrupted, cancelled, and failed restores cannot partially replace current data. | 4 | Passed |
| P9-07 | Clear, reinstall, and recovery | Clear All Data, clean reinstall, and restore recovery behave as documented. | 4 | Passed |
| P9-08 | Financial integrity | Balances and income/expense totals remain exact integer-centavo calculations. | 4 | Passed |
| P9-09 | Large-dataset stability | Startup, history loading, scrolling, search, combined filters, and saving remain correct and usable with at least 10,000 transactions. | 3 | Passed |
| P9-10 | Responsive layouts | Supported narrow and larger phone profiles have no clipped, overlapping, or inaccessible controls. | 3 | Passed |
| P9-11 | Enlarged fonts | Core workflows remain readable and usable at the supported enlarged-font setting. | 3 | Passed |
| P9-12 | Accessibility | Important states do not rely on color alone; labels, focus, Back behavior, and touch targets remain usable. | 3 | Passed |
| P9-13 | Defect regression | All critical and high-severity defects are resolved and the complete automated suite passes. | 3 | Pending |
| P9-14 | Documentation and identity | License, README, roadmap, architecture, database guide, changelog, release notes, screenshots, and version values match `v1.0.0`. | 4 | Pending |
| P9-15 | Release candidate | APK signature, alignment, package contents, API levels, ABIs, checksum, clean installation, and official upgrade all pass. | 5 | Pending |

## Defect Policy

- Critical and high-severity defects block `v1.0.0`.
- Medium and low-severity defects must be fixed or explicitly documented as accepted limits.
- Every correction requires focused verification followed by the complete regression suite before closeout.

## Clean Installation and First Use

Passed on July 27, 2026.

- Device: `Xiaomi 2312DRA50G`
- Android: `16` (API `36`)
- APK: `Enkryon-v0.8.0.apk`
- The clean installation and first launch completed without errors.
- All empty states, six-screen navigation, Back behavior, and invalid-form protection passed.
- The controlled income of `₱1,234.56` and expense of `₱10.21` produced income of `₱1,234.56`, expenses of `₱10.21`, and balance of `₱1,224.35`.
- Accounts, categories, transactions, notes, and totals persisted after force-stop and relaunch.
- Complete automated regression: `499 passed`.

## Legacy Database Migration Verification

Passed on July 27, 2026.

- The retained `v0.3.0` fixture upgraded through migrations 1–4.
- A `v0.7.0` fixture generated from official source commit `8ddc6e9`
  upgraded from migration version 3 to version 4.
- All record counts, IDs, relationships, notes, dates, and SQLite
  sequences remained unchanged.
- Income remained `123456` centavos, expenses remained `1021` centavos,
  and balance remained `122435` centavos.
- Foreign-key validation passed.
- All three transaction-history indexes were created correctly.
- A second migration run made no additional changes.
- Focused migration regression: `13 passed`.
- Complete automated regression: `500 passed`.

## Core, Backup, and Recovery Verification

Passed on July 28, 2026.

- Device: `Xiaomi 2312DRA50G`
- Android: `16` (API `36`)
- Core account, category-group, category, and transaction creation, editing, deletion, search, filtering, Reset All, and relaunch persistence passed.
- Temporary transaction totals changed to income of `₱1,234.56`, expenses of `₱210.23`, and balance of `₱1,024.33`; deleting the temporary records restored the original totals.
- Backup SHA-256: `0741aaf7a387f29c4a88a750d71bf42f154f15a09c3e709a37f18ec89cdfa362`
- Restore preview contained `1` account, `2` category groups, `2` categories, `2` transactions, and `7` total records.
- Backup round-trip comparison: `ROUND TRIP: PASS`.
- Export cancellation preserved the existing data.
- Clear All Data produced empty screens and zero totals.
- The verified backup restored all records, relationships, notes, dates, and exact totals.
- Malformed, incompatible, corrupted, and cancelled restore attempts were rejected without changing current data.
- Clean reinstallation produced an empty profile; backup recovery and force-stop/relaunch persistence passed.
- Focused backup and recovery regression: `53 passed`.
- Complete automated regression: `500 passed`; branch coverage `81%`.

## Large-Dataset Stability Verification

Passed on July 28, 2026.

- Device: `Xiaomi 2312DRA50G`
- Android: `16` (API `36`)
- The scale profile contained `1` account, `2` category groups, `2` categories, `10,000` transactions, and `10,005` total records.
- Dashboard totals remained income of `₱100,000.00`, expenses of `₱50,000.00`, and balance of `₱50,000.00`.
- Transaction History loaded and scrolled responsively without freezing.
- Exact search, date-range filtering, combined filtering, Reset All, and relaunch persistence passed.
- Transaction History was virtualized with `RecycleView` after the original implementation exhausted device memory by creating 10,000 complete card widgets.
- Recycled card data, actions, colors, and fixed row heights remained correct.
- First-entry spacing remained stable after waiting, scrolling, filtering, and re-entering.
- The complete automated regression passed with `504` tests after both corrections.
- Creating a temporary `₱0.01` expense remained responsive, persisted after force-stop and relaunch, and deleting it restored the original scale totals.
- The virtualization-focused suite passed `80` tests, and the row-height-focused suite passed `54` tests.
- The rebuilt APK passed checksum and signature verification; desktop and Android application checks also passed.

## Display and Accessibility Verification

Passed on July 28, 2026.

- Device: `Xiaomi 2312DRA50G`
- Android: `16` (API `36`)
- The narrow `S / 90%`, larger-phone default-font, and enlarged-font display profiles passed.
- The enlarged-font profile was tested at `200%`, exceeding the required minimum of `130%`.
- All six screens remained usable without clipped, overlapping, clustered, or inaccessible controls.
- Navigation, scrolling, long content, transaction cards, filters, Add Transaction controls, and Settings actions remained readable and reachable.
- Income and expenses remained distinguishable through text, icons, and amount signs rather than color alone.
- Selected filters, input labels, touch targets, and keyboard interactions remained usable.
- Android Back dismissed an open selector or dialog before navigating away.
- The destructive confirmation remained readable and was cancelled without changing data.

## Version 1.0 Release-Candidate Preparation

Prepared on July 28, 2026; final verification remains pending.

- The application version source, Android artifact name, changelog, roadmap,
  README, and release notes were advanced to `1.0.0`.
- A proprietary source-code license permits viewing and portfolio evaluation
  while withholding permission to copy, modify, distribute, or reuse the
  repository materials.
- Architecture, database, testing, and release documentation were updated to
  describe the shipped search, migration, backup, virtualization, and
  large-history behavior.
- The real Settings screenshot, complete post-change regression, GitHub
  Actions run, signed artifact evidence, clean installation, and official
  `v0.8.0` in-place upgrade remain required.
- `P9-13`, `P9-14`, and `P9-15` remain pending until their complete evidence
  is recorded.
