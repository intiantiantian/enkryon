# Phase 3 Verification Report

Date: 2026-07-17
Branch: `phase-3-automatic-quality-checks`
Base release: `v0.4.0`

## Objective

Make every change repeatably testable in the verified local environment
and on GitHub so financial, migration, and service regressions are visible
before release preparation.

## Result

Phase 3 local, continuous-integration, legacy-upgrade, coverage, and
desktop smoke verification passed.

The automated suite grew from 88 to 99 tests. GitHub Actions now installs
the pinned development environment, compiles the source, and runs all tests
with branch coverage on pushes, pull requests, and manual workflow runs.

## Completed Checkpoints

### Reproducible development environment

- Added `requirements-dev.txt` for runtime and development dependencies.
- Verified Python 3.13.14 and pytest 9.1.1.
- Added pytest-cov 7.1.0.
- Documented local setup and required checks.

### Automatic GitHub checks

- Added `.github/workflows/quality.yml`.
- Configured push, pull-request, and manual triggers.
- Added Python source compilation.
- Added the complete test suite with coverage output.
- Limited workflow permissions to repository-content reads.

The first hosted run stalled because the Windows runner exposed OpenGL
1.1, while Kivy requires OpenGL 2.0 for real rendering. The workflow now
uses Kivy's always-available mock graphics backend for headless tests. This
setting does not affect desktop or Android rendering.

### Legacy database integration test

- Added a saved `v0.3.0` SQLite fixture.
- Copied the fixture before each upgrade test so the historical file stays
  unchanged.
- Verified all three migrations run once and remain safe to rerun.
- Preserved accounts, category groups, categories, transaction IDs,
  relationships, dates, notes, centavo values, totals, and balance.

### Service and failure-path tests

- Tested all transaction-list empty states.
- Tested account, transaction-type, and limit forwarding.
- Tested transaction-list response composition.
- Verified repository read errors remain visible.
- Updated deletion services to preserve repository success or failure.

### Coverage and application smoke testing

- Added application-wide branch-coverage configuration.
- Recorded an initial coverage baseline of 51%.
- Added a headless import smoke test for the application entry point and
  all six screens.
- Completed a manual desktop navigation smoke test.

### Documentation

- Corrected stale Phase 1.2 observations.
- Expanded the database and migration guide.
- Repaired Phase 2 verification formatting.
- Added local test, coverage, and GitHub Actions instructions.
- Added and linked the complete repository roadmap.

## Final Verification

```text
99 passed
TOTAL coverage: 51%
Python compilation: passed
Git whitespace check: passed
Working tree before closeout: clean
Desktop navigation smoke check: passed
GitHub Actions: passed
```

The desktop smoke check covered:

- Dashboard
- Accounts
- Categories
- Add Transaction
- Transaction History
- Settings

## Coverage Priorities

Coverage is strongest around the highest-risk financial foundation:

| Area | Final coverage |
|---|---:|
| Database migrations | 88% |
| Transaction repository | 86% |
| Transaction services | 100% |
| Money utilities | 85% |
| Transaction payload | 100% |
| Transaction validation | 100% |

The overall 51% baseline is informational rather than a release threshold.
Future tests should target meaningful uncovered behavior, especially screen
coordination and interactive widgets, rather than increasing the number for
its own sake.

## Known Limits Assigned to Later Phases

- Detailed screen and widget interaction testing remains in Phase 6.
- Transaction creation and editing are still primarily coordinated by the
  add-transaction screen; service extraction remains in Phase 5.
- Android release reproduction, upgrade testing, and packaging hardening
  remain in Phase 4.
- Backup and restore remain in Phase 7.

## Completion Gate

Phase 3 is complete because:

- the pinned development setup runs locally and on a fresh GitHub runner;
- pushes and pull requests receive automatic compilation, test, and
  coverage checks;
- a saved older database upgrades without data loss;
- service success and failure paths have direct tests;
- the full local and GitHub suites pass; and
- the desktop navigation regression check passes.

Phase 4 — Reliable Android Releases is next.
