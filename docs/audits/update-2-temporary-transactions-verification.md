# Update 2 Temporary Transactions Verification

Updated: August 5, 2026

## Current Checkpoint

- Target release: `v1.2.0`.
- Branch: `update-2-temporary-transactions`.
- Verified weighted progress: `7%`.
- Current task: Task 1 complete — status semantics and baseline locked.

## Weighted Plan

| Task | Weight | Verification state |
|---:|---:|---|
| 1. Lock status semantics and baseline | 7% | Verified |
| 2. Add migration and status-aware persistence | 18% | Not started |
| 3. Add form state and service workflows | 18% | Not started |
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

## Next Gate

Task 2 may begin only after the contract documentation tests, complete suite,
Python compilation, Git whitespace check, changed-file review, and checkpoint
commit pass. Task 2 will add migration 6 and status-aware persistence without
changing migrations 1 through 5.
