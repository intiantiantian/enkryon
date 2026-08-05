# Update 2 Temporary Transactions Verification

Updated: August 5, 2026

## Current Checkpoint

- Target release: `v1.2.0`.
- Branch: `update-2-temporary-transactions`.
- Verified weighted progress: `35%`.
- Current task: Task 3A complete — form state and temporary save/edit
  workflows verified.

## Weighted Plan

| Task | Weight | Verification state |
|---:|---:|---|
| 1. Lock status semantics and baseline | 7% | Verified |
| 2. Add migration and status-aware persistence | 18% | Verified |
| 3. Add form state and service workflows | 18% | In progress (10% verified) |
| 4. Build temporary transaction interface | 20% | Not started |
| 5. Integrate balances, totals, and activity filters | 16% | Not started |
| 6. Extend backup and recovery | 11% | Not started |
| 7. Close and release Update 2 | 10% | Not started |

## Verified v1.1.0 Baseline

The clean `v1.1.0` source baseline was verified before feature implementation:

- Python: `3.13.14` on `win32`.
- pytest: `9.1.1`.
- pytest-cov: `7.1.0`.
- Complete suite: `637 passed in 16.45s`.
- Recorded total branch coverage: `83%`.
- Python compilation: passed.
- Git whitespace check: passed.
- Working tree after the baseline checks: clean.

No migration, repository, service, screen, widget, KV, or backup implementation
changed during Task 1.

## Locked Product Decisions

- A temporary transaction keeps its income or expense type and adds
  `posting_status = 'temporary'`.
- A temporary record is fully non-posting and cannot affect account balances,
  Income, Expenses, category totals, net cash flow, or statistical financial
  aggregates.
- Existing transactions upgrade as `posted`.
- Posting changes the existing record atomically; it does not copy the record.
- Failed or repeated posting cannot alter the status or posted totals.
- Temporary records remain visible and searchable in Dashboard recent activity
  and Activity History with a non-color-only `Temporary` label.
- Income and Expense filters remain posted-only; the Temporary filter covers
  temporary income and expense records.
- Referenced accounts, categories, and category groups remain protected.
- Migration 6 extends `transactions`; backup format 3 preserves posting status;
  format-1 and format-2 transactions restore as posted.
- The first release has no automatic posting or expiration.

## Release Exception

The release-owner waiver for the missing official physical-device
`v1.0.0`-to-`v1.1.0` in-place upgrade test remains explicit. Automated
migration tests passed, but the Android upgrade is not described as verified.

Until the exception is closed, the documented upgrade precaution is to export
a backup first. The `v1.1.0`-to-`v1.2.0` official in-place upgrade remains a
required Update 2 release gate.

## Task 2 Persistence Evidence

Task 2 was completed in two checkpoints:

- Task 2A added migration 6, the constrained posting status, status-aware
  transaction records and CRUD, compare-and-set posting, status-preserving
  restore, posted-only totals and balances, relationship protection, and
  database-version-6 compatibility. Its complete gate reported `653 passed`
  with `83%` total branch coverage.
- Task 2B added the query-plan-justified
  `transactions_posting_status_history_index`, verified its exact columns on
  fresh and upgraded databases, and extended the 10,000-record history
  regression to prove status-filtered newest-first retrieval uses the index
  without a temporary ordering table. Its complete gate reported `654 passed`
  with `83%` total branch coverage.

Both checkpoints passed Python compilation and Git whitespace checks. No
real-application check was required because Task 2 introduced no user-visible
workflow. Migrations 1 through 5 remained unchanged.

## Task 3A Form-State and Save/Edit Evidence

Task 3A added one shared posting-status vocabulary, extended transaction form
state to preserve `posted` or `temporary`, and passed that status through the
UI-independent save contract. New records can now be saved explicitly as
temporary, while edits preserve the existing status and reject attempts to
change status through the ordinary save path. Posting remains a separate
workflow.

The service now rejects unknown status values and invalid date/time input before
repository access, preserves exact integer-centavo payloads, distinguishes
temporary save/edit results, handles missing records, and converts repository
exceptions into stable failure results. The focused Task 3A gate contains `61`
tests. The complete checkpoint gate is expected to report `666 passed` with
approximately `83%` total branch coverage.

No real-application check is required for Task 3A because it adds no visible
control yet. Task 4 will connect these service and form-state capabilities to
the temporary-transaction interface.

## Next Gate

Task 3B will add UI-independent posting, delete, and restore workflows for
temporary transactions. Posting must remain atomic and compare-and-set
protected, repeated posting must be rejected, and repository failures must leave
status and totals unchanged.
