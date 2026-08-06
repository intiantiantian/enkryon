# Update 2 Pending Transactions Verification

Updated: August 6, 2026

## Current Checkpoint

- Target release: `v1.2.0`.
- Branch: `update-2-temporary-transactions`.
- Verified weighted progress: `99%`.
- Current task: Task 7B Android, upgrade, recovery, artifact, and approval
  evidence are verified. Only merge, tag, and GitHub Release publication
  remain.

## Weighted Plan

| Task | Weight | Verification state |
|---:|---:|---|
| 1. Lock status semantics and baseline | 7% | Verified |
| 2. Add migration and status-aware persistence | 18% | Verified |
| 3. Add form state and service workflows | 18% | Verified |
| 4. Build pending transaction interface | 20% | Verified |
| 5. Integrate balances, totals, and activity filters | 16% | Verified |
| 6. Extend backup and recovery | 11% | Verified |
| 7. Close and release Update 2 | 10% | In progress — 9% verified; publication remains |

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

- A pending transaction keeps its income or expense type and adds
  `posting_status = 'temporary'`.
- A pending record is fully non-posting and cannot affect account balances,
  Income, Expenses, category totals, net cash flow, or statistical financial
  aggregates.
- Existing transactions upgrade as `posted`.
- Posting changes the existing record atomically; it does not copy the record.
- Failed or repeated posting cannot alter the status or posted totals.
- Pending records remain visible and searchable in Dashboard recent activity
  and Activity History with a non-color-only `Pending` label.
- Income and Expense filters remain posted-only; the Pending filter covers
  pending income and expense records.
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
pending save/edit results, handles missing records, and converts repository
exceptions into stable failure results. The focused Task 3A gate contains `61`
tests. The complete checkpoint gate reported `666 passed` with `83%` total branch
coverage.

No real-application check is required for Task 3A because it adds no visible
control yet. Task 4 will connect these service and form-state capabilities to
the pending-transaction interface.

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

Delete and restore workflows now distinguish pending records while preserving
the complete transaction record for the existing undo flow. Repository lookup,
delete, and restore failures return stable service results, and an integration
round trip proves that deletion and restoration do not make a pending record
financially effective. The focused Task 3B gate contains `89` tests. The complete Task 3 gate
reported `682 passed` with approximately `83%` total branch coverage. A
warning-only follow-up closed the directly opened SQLite test connection, and
the complete suite again reported `682 passed` with no warning.

No real-application check was required for Task 3B because it added no visible
control. Task 4 connects these verified workflows to the interface.

## Task 4A Form Actions Evidence

Task 4 is split into two weighted checkpoints: Task 4A contributes `11%` for
the transaction-form interface, and Task 4B contributes `9%` for pending
status and posting actions in Dashboard recent activity and Activity History.

Task 4A replaces the icon-only save control with explicit `Save as Pending`
and `Post Transaction` buttons. New, pending-edit, and posted-edit states use
different titles, status labels, guidance text, and action labels. Posted edits
show `Already Posted` as a disabled secondary action rather than permitting a
status reversal.

When an edited pending transaction is posted, the screen first validates and
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

Pending cards show a clock icon and explicit `PENDING` text, so status is
not communicated by color alone. Only pending transaction cards expose the
direct post action. Posted transactions and transfers cannot invoke that card
action. The post confirmation states that the transaction becomes financially
effective immediately and that account balances and totals will update.

Pending deletion uses distinct confirmation text explaining that the record
does not currently affect financial totals. A successful direct post refreshes
the full Dashboard summary and recent activity together; Activity History uses
its normal virtualized refresh. Service failure and stale-card double-post
results remain stable and do not trigger a success refresh.

The focused Task 4B gate covers status-aware Activity records, recycled-card
state, direct posting, confirmation and deletion copy, responsive card height,
non-color-only semantics, and Dashboard refresh behavior. The complete Task 4 gate reported `707 passed` with approximately `83%` total
branch coverage. Real-application Dashboard and Activity History checks passed
before commit `7513072`. Task 4B raised verified progress to `63%`.

## Task 5 Activity and Financial Integration Evidence

Task 5 adds a separate posting-status dimension to shared activity filter state.
The Dashboard and Activity History now expose an explicit `PENDING` filter.
Selecting `Income` or `Expense` sets `posting_status = 'posted'`, while selecting
`Pending` sets `posting_status = 'temporary'` without fabricating a transaction
type. `All` continues to include posted transactions, pending transactions, and
transfers in one stable newest-first history.

The activity repository applies posting status before the unified result is
ordered. Income and Expense repository queries default to posted-only behavior,
Pending excludes transfers, and Pending can still combine with account, group,
category, search, and inclusive date filters. Empty states distinguish Pending
from Income, Expense, Transfer, and general no-match results.

A controlled mixed-data integration proves that pending income and expense
records remain absent from account balances, Income, Expenses, and all-account
net totals until posting. Posting moves the existing record from the Pending
view to the correct posted Income or Expense view exactly once; a repeated post
is rejected without a second financial effect. Dashboard posting refreshes both
the financial summary and recent activity, while Activity History refreshes its
virtualized list.

The large-history regression seeds `10,000` mixed posted and pending
transactions. The Pending activity query returns the correct newest records,
uses `transactions_posting_status_history_index`, and does not create a
temporary ordering B-tree. The focused Task 5 gate covers repository semantics,
service forwarding, filter state, Dashboard and history controls, responsive
layout, accessibility text, exact financial invariants, posting refresh, and
query plans. The complete checkpoint reported `725 passed` with approximately `83%` total
branch coverage. Real-application filter checks passed before commit `6775eac`.

## Task 6 Backup and Recovery Evidence

Task 6 advances the user-controlled document format from version 2 to version
3. Format-3 transaction records include `posting_status`, so posted and Pending
records survive export, Clear All Data, replacement restore, and a fresh
connection without changing identity, relationships, or financial semantics.
Account transfers remain first-class backup records.

Validation remains version-specific. Format 1 accepts its original four record
collections, format 2 accepts transfers without posting status, and format 3
requires an exact `posted` or `temporary` value on every transaction. Format-1
and format-2 documents normalize to the current format before restore: missing
transfers become an empty collection and every older transaction becomes
`posted`. Missing, blank, differently-cased, or unknown format-3 statuses are
rejected before the current database is modified.

The recovery regression covers exact record counts, transaction and transfer
IDs, SQLite sequences, foreign-key checks, integrity checks, replacement
rollback, and posted-only financial totals. A controlled mixed document proves
that a Pending expense remains excluded from Expenses and account balances
after a format-3 round trip. The same records converted to format 1 or format 2
restore as posted, matching the locked compatibility contract.

The focused Task 6 recovery gate contains `82` tests. The complete checkpoint
reported `737 passed` with approximately `83%` total branch coverage. Python
compilation and Git whitespace checks passed. The supplied real-application log records a successful application launch
before commit `f060d35`. The complete Android backup, Clear All Data,
format-3 restore, status-preservation, and relaunch cycle remains part of the
final Task 7B release gate. Task 6 raised verified progress to `90%`.

## Terminology Correction Evidence

The user-facing feature name is **Pending Transactions**. The persisted
`posting_status = 'temporary'` value, branch name, historical file paths, and
internal helper identifiers remain unchanged to avoid unnecessary migration and
code churn. Form labels, card badges, confirmations, service result messages,
documentation, and future filters use `Pending`.

The originally requested pass-through cash-out scenario is documented as a
separate future feature because it changes account balances while remaining
outside Income and Expenses.

## Task 7A Release Candidate Evidence

Task 7A advances the canonical application version to `1.2.0` and prepares the
source-controlled release identity without claiming that the Android release is
already complete. README, changelog, roadmap, release guide, architecture,
database guide, Android checklist, release notes, and closeout tests agree on
Pending Transaction semantics, migration 6, backup format 3, and the standard
`Enkryon-v1.2.0.apk` artifact name.

The candidate release notes deliberately mark GitHub Actions, signing,
alignment, installation, official upgrade, smoke testing, artifact size, and
checksum as pending. Those values must be replaced only with observed evidence.
The desktop gate repeats the complete test suite with coverage, Python
compilation, Git whitespace checks, version consistency, and documentation
contracts. Task 7A contributes `4%` and raises verified progress to `94%`.

## Task 7B Final Android and Recovery Evidence

The final verified application checkpoint before release-evidence documentation
is commit `0b9da6a` on `update-2-temporary-transactions`. Its complete local
gate reported
`746 passed in 21.09s` with `83%` total branch coverage. Python compilation,
Git whitespace checks, focused interface tests, real-application checks, and
GitHub Actions all passed.

The verified Windows source was synchronized one-way into the WSL Buildozer
copy. A checksum-mode rsync dry run produced no output, and the WSL copy
reported application version `1.2.0` plus the final collapsible Advanced
Filters implementation.

The secure release helper built and verified `Enkryon-v1.2.0.apk` using the
permanent Enkryon signing identity. Signature and zip-alignment checks passed.
The final artifact is `45,770,820` bytes with SHA-256
`b5e1942d160d19c78604c84099d203972f9f886dc66e49a1c66eaee3e2aebdc3`.
The checksum passed in WSL and again after copying the APK to Windows.

A clean physical-device installation passed on Xiaomi `2312DRA50G` running
Android 16 / API 36. Android reported package `com.intian.enkryon`, version
name `1.2.0`, version code `102410200`, minimum API 24, and target API 36.
Launch, Activity History collapse/reset behavior, Advanced Filters layout,
and Pending controls passed.

For the official upgrade gate, an official v1.1.0 installation restored a
legacy JSON dataset before `adb install -r` installed v1.2.0 without clearing
application data. Accounts, groups, categories, transactions, transfers,
notes, dates, balances, and exact centavo values remained intact. Pending
creation, one-time posting, force-stop, and relaunch persistence passed.

The final recovery gate exported a v1.2.0 format-3 JSON document containing a
recognizable Pending transaction, then performed uninstall, clean reinstall,
replacement restore, Pending-filter verification, one-time posting, force-stop,
and relaunch. Posted/Pending state, legacy records, relationships, notes,
amounts, and balances were preserved. The release owner approved the observed
results.

## Final Publication Gate

Merge the verified branch into `main`, confirm the merge commit receives green
GitHub Actions, create and push annotated tag `v1.2.0`, publish the GitHub
Release with the verified APK, checksum sidecar, and release notes, and verify
the public assets and checksum. Completion of that gate raises Update 2 from
`99%` to `100%`.
