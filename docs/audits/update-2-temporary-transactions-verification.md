# Update 2 Temporary Transactions Verification

Updated: August 5, 2026

## Current Checkpoint

- Target release: `v1.2.0`.
- Branch: `update-2-temporary-transactions`.
- Verified weighted progress: `63%`.
- Current task: Task 4 complete — explicit form actions, Temporary activity
  treatment, and guarded direct posting are implemented; Task 5 activity
  filters and financial integration are next.

## Weighted Plan

| Task | Weight | Verification state |
|---:|---:|---|
| 1. Lock status semantics and baseline | 7% | Verified |
| 2. Add migration and status-aware persistence | 18% | Verified |
| 3. Add form state and service workflows | 18% | Verified |
| 4. Build temporary transaction interface | 20% | Verified |
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
tests. The complete checkpoint gate reported `666 passed` with `83%` total branch
coverage.

No real-application check is required for Task 3A because it adds no visible
control yet. Task 4 will connect these service and form-state capabilities to
the temporary-transaction interface.

## Task 3B Post/Delete/Restore Evidence

Task 3B added a dedicated UI-independent posting service that loads the current
record, rejects missing and already-posted transactions, and performs one
compare-and-set transition from `temporary` to `posted`. Successful posting
changes the existing record once, so exact posted totals and account balances
become effective immediately without copying or rebuilding the transaction.

The posting workflow converts lookup and repository exceptions into stable
results. An induced SQLite trigger failure proves that an unsuccessful status
update leaves the record temporary and leaves posted totals and balances
unchanged. Repeated posting is rejected before a second repository write.

Delete and restore workflows now distinguish temporary records while preserving
the complete transaction record for the existing undo flow. Repository lookup,
delete, and restore failures return stable service results, and an integration
round trip proves that deletion and restoration do not make a temporary record
financially effective. The focused Task 3B gate contains `89` tests. The complete Task 3 gate
reported `682 passed` with approximately `83%` total branch coverage. A
warning-only follow-up closed the directly opened SQLite test connection, and
the complete suite again reported `682 passed` with no warning.

No real-application check was required for Task 3B because it added no visible
control. Task 4 connects these verified workflows to the interface.

## Task 4A Form Actions Evidence

Task 4 is split into two weighted checkpoints: Task 4A contributes `11%` for
the transaction-form interface, and Task 4B contributes `9%` for temporary
status and posting actions in Dashboard recent activity and Activity History.

Task 4A replaces the icon-only save control with explicit `Save as Temporary`
and `Post Transaction` buttons. New, temporary-edit, and posted-edit states use
different titles, status labels, guidance text, and action labels. Posted edits
show `Already Posted` as a disabled secondary action rather than permitting a
status reversal.

When an edited temporary transaction is posted, the screen first validates and
saves the current fields without changing status. It then calls the dedicated
compare-and-set posting workflow. A validation or save failure prevents the
post attempt; a posting failure keeps the edited record temporary and leaves
all posted totals unchanged.

The form action group stacks on constrained screens, expands with system font
scale, and communicates status through visible text rather than color alone.
The focused Task 4A gate contains `82` tests. The complete checkpoint gate is
recorded as `696 passed` with approximately `83%` total branch coverage. Task
4A raised verified progress to `54%`. The supplied execution log records a
successful application launch under Python 3.13.14, Kivy 2.3.1, and KivyMD
1.2.0 before commit `0358ef5`.

## Task 4B Activity Interface Evidence

Task 4B carries posting status through unified Activity records. Transaction
activity retains its stored `posted` or `temporary` value, while transfer
activity uses the shared posted-only card contract. Dashboard recent activity
and virtualized Activity History therefore render the same status data without
performing a second repository lookup per card.

Temporary cards show a clock icon and explicit `TEMPORARY` text, so status is
not communicated by color alone. Only temporary transaction cards expose the
direct post action. Posted transactions and transfers cannot invoke that card
action. The post confirmation states that the transaction becomes financially
effective immediately and that account balances and totals will update.

Temporary deletion uses distinct confirmation text explaining that the record
does not currently affect financial totals. A successful direct post refreshes
the full Dashboard summary and recent activity together; Activity History uses
its normal virtualized refresh. Service failure and stale-card double-post
results remain stable and do not trigger a success refresh.

The focused Task 4B gate covers status-aware Activity records, recycled-card
state, direct posting, confirmation and deletion copy, responsive card height,
non-color-only semantics, and Dashboard refresh behavior. The complete Task 4
gate is expected to report `707 passed` with approximately `83%` total branch
coverage. Real-application Dashboard and Activity History checks are required
before committing Task 4B.

## Next Gate

Task 5 will add the explicit `Temporary` filter, make Income and Expense
filters posted-only, verify search/account/category/date combinations, prove
conversion refreshes every relevant total and list, and repeat the 10,000-row
performance gate with mixed posted and temporary activity.
