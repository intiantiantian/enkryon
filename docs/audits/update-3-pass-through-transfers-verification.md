# Update 3 Pass-through Transfers Verification

## Baseline

- Release baseline: `v1.2.0`.
- Branch: `update-3-pass-through-transfers`.
- Python: `3.13.14` on Windows.
- Complete baseline: `746 passed in 32.69s`.
- Recorded total branch coverage: `83%`.
- Working tree was clean before the branch was created.

## Weighted Progress

| Task | Weight | State |
|---|---:|---|
| 1. Lock pass-through contract and baseline | 9% | Completed — `c7d0fd1` |
| 2. Add migration and transfer-kind persistence | 18% | Completed — `1354c5a` |
| 3. Add pass-through service workflows | 17% | Completed — `2814e98` |
| 4. Build pass-through transfer interface | 18% | Completed — `e6c68d7` |
| 5. Integrate balances, activity, search, and filters | 16% | Completed — `05b635c` |
| 6. Extend backup, recovery, and performance | 12% | Completed - `01299eb` |
| 7. Close and release Update 3 | 10% | Completed - balance-neutral release |
| **Total** | **100%** | **Released as v1.3.0** |

## Task 1 Contract Decisions

- Canonical exchange: friend deposits to Bank while the user gives equivalent
  Cash; store Cash as the account outflow and Bank as the account inflow.
- Pass-through principal is equal and opposite across the two accounts and is
  net zero across all accounts.
- Pass-through principal never changes Income, Expenses, category totals, or
  posted net cash flow.
- Migration 7 extends `account_transfers` with `transfer_kind`; existing rows
  normalize to `internal`.
- `pass_through` is the persisted kind for the new workflow.
- Counterparty is optional; purpose/details remain in Notes for v1.3.0.
- A real service fee is a separate posted Expense.
- Primary Transfer filtering includes both kinds; Advanced Filters distinguish
  Internal from Pass-through.
- Backup format 4 preserves transfer kind and counterparty while formats 1–3
  normalize older transfers to Internal.
- Partial settlement, loans, debts, receivables, split counterparties, and
  multi-leg exchanges are excluded from the first release.

Task 1 changes documentation and contract tests only. Its focused contract
gate reported `5 passed`; the complete suite reported `751 passed` with `83%`
coverage. Compilation and `git diff --check` passed, and the verified checkpoint
was committed as `c7d0fd1` (`Define pass-through transfer contract`).

## Task 2 Persistence Work

Task 2 adds migration 7 as `account_transfer_kinds`. The migration extends the
existing `account_transfers` table with constrained `transfer_kind` and optional
trimmed `counterparty` columns. Existing records take the safe `internal`
default; the only stored kinds are `internal` and `pass_through`.

`TransferRecord` and the existing transfer repository carry both fields while
keeping old repository callers backward-compatible through `internal`/`None`
defaults. Create, read, update, delete, restore, account filtering, kind
filtering, stable newest-first ordering, and invalid-kind/counterparty behavior
receive focused persistence coverage.

No new transfer-kind index is introduced. The existing history-order index
continues to cover unfiltered newest-first access, and the released source and
destination indexes remain intact. A dedicated kind index stays deferred until
later activity/filter query plans demonstrate that it is useful.

Backup format remains 3 during this checkpoint. Its validator accepts database
migration version 7 so existing development export/restore tests remain valid,
but format 3 intentionally does not claim to preserve Pass-through metadata.
Task 6 remains responsible for backup format 4 and exact kind/counterparty
round-trip recovery before v1.3.0 can ship.

Task 2 Windows verification reported `124 passed` for the focused gate and
`761 passed` for the complete suite with `84%` total branch coverage. Python
compilation and `git diff --check` passed. The checkpoint was committed as
`1354c5a` (`Add pass-through transfer persistence`).

## Task 3 Service Workflow Work

Task 3 carries `transfer_kind` and optional `counterparty` through the existing
transfer service and form-state path. New saves remain Internal by default, while
Pass-through create/edit operations explicitly preserve `pass_through` metadata
and trim blank/whitespace counterparty input to no counterparty. Invalid transfer
kinds and non-text counterparty values fail before repository access.

`TransferFormState.from_transfer()` and `to_save_arguments()` preserve kind and
counterparty during editing. This prevents a Pass-through record from silently
becoming Internal while the Task 4 interface controls are still being added.

Focused workflow coverage locks exact centavos, the canonical Cash-to-Bank
direction, equal-and-opposite participating-account effects, zero all-account
change, zero Income/Expense change, edit reversal/reapplication, delete/undo
restore, stable failed updates, same-account rejection, missing/invalid metadata,
and ordinary Internal-transfer compatibility.

Task 3 Windows verification reported `91 passed` for the focused gate and
`777 passed` for the complete suite with `84%` total branch coverage. Python
compilation and `git diff --check` passed. The checkpoint was committed as
`2814e98` (`Add pass-through transfer workflows`).

## Task 4 Interface Work

Task 4 exposes the already-verified transfer kind through explicit `INTERNAL`
and `PASS-THROUGH` controls on the existing Transfer screen. The selected kind
is communicated with visible text as well as button styling. Pass-through mode
shows explicit linked account outflow/inflow guidance and states that principal
is not Income or Expense.

The optional counterparty control is shown only for Pass-through mode. Its
dialog preserves user-entered text in form state while the visible label is
trimmed for presentation; persistence remains responsible for final
normalization. Switching to Internal clears Pass-through-only counterparty state
so ordinary transfers cannot accidentally inherit that metadata through the
interface.

The mode selector stacks on constrained widths and enlarged font settings,
guidance text grows vertically instead of truncating, and the counterparty
control uses the shared 56dp/font-scaled touch target. Edit loading continues to
preserve and visibly restore Pass-through kind and counterparty metadata.


## Task 5 Activity and Filter Integration Work

Task 5 carries `transfer_kind` and optional `counterparty` through the unified
activity query and `ActivityRecord`. General Transfer activity continues to
include both Internal and Pass-through records, while a dedicated kind filter
can select either `internal` or `pass_through` without creating a second
activity subsystem. Transaction rows expose no transfer metadata.

Transfer search now includes source account, destination account, notes,
counterparty, and the visible `Internal`/`Pass-through` kind name. Existing
account and date filters compose with transfer kind while stable newest-first
ordering remains unchanged. Category-only filters continue to exclude transfer
activity.

Activity History moves the general `TRANSFER` control into the primary filter
row. Advanced Filters provide explicit `INTERNAL` and `PASS-THROUGH` controls
alongside `PENDING`. The active-filter summary uses the ASCII ` | ` separator
rather than a decorative Unicode bullet so UI text is less dependent on glyph
coverage.

Shared activity cards label Pass-through records with visible `PASS-THROUGH`
text and `Pass-through Transfer`, present the linked effects as account outflow
and inflow, and show `Counterparty: <name>` when present. Because Dashboard recent activity uses
the same activity/card path, the same non-color-only Pass-through treatment is
shown there without adding extra Dashboard filter controls. Recycled transaction
cards explicitly clear transfer-kind/counterparty state.

Release closeout further clarifies the Task 4/5 copy: Pass-through should not
look like an Internal Transfer of the same physical money. User-facing Kivy copy
uses explicit linked effects such as `Cash outflow | Bank inflow` and otherwise
prefers plain ASCII wording when a decorative symbol is unnecessary.

No transfer-kind index is added in Task 5. Task 6 remains responsible for the
large-history/query-plan gate and may add an index only if measured plans justify
it.


## Task 5 Verification Note

The Task 5 Windows gate, real-app checks, compilation, and whitespace checks were
reported as passed before commit `05b635c` (`Integrate pass-through activity
semantics`). The terminal was cleared with `cls` before the exact pytest summary
was retained, so this audit does not invent a focused/full test count. The clean
post-commit working tree is the recorded checkpoint state.

## Task 6 Backup, Recovery, and Performance Work

Task 6 advances new exports from backup format 3 to backup format 4. Format 4
adds exact `transfer_kind` and optional `counterparty` fields to every
`account_transfers` backup row while preserving the existing format-3
`posting_status` field on transactions.

The validator continues accepting formats 1 through 4. Formats 1 and 2 normalize
transactions to `posted`; format 3 preserves its exact posted/Pending status. All
formats before 4 normalize restored transfers to `transfer_kind = 'internal'`
and `counterparty = NULL`, so old backups cannot accidentally become
Pass-through activity. Current format-4 kind values are constrained to
`internal` or `pass_through`, and a non-null counterparty must be non-empty and
trimmed before replacement restore begins.

Replacement restore remains atomic and keeps its existing record-count, ID
sequence, foreign-key, and integrity verification. Focused recovery coverage
adds exact format-4 Internal/Pass-through round trips, malformed metadata
rejection before replacement, formats 1/2/3 compatibility, Clear All Data and
relaunch-safe persistence semantics, and a 10,000-transfer mixed-history
round-trip.

The 10,000-transfer query-plan check continues to use the existing
`account_transfers_history_order_index` for newest-first Pass-through results
without a temporary ORDER BY B-tree. No dedicated transfer-kind index is added
because the measured access path remains adequate at this checkpoint.

## Task 6 Verification Evidence

Windows verification reported `103 passed` for the focused backup/recovery gate.
After a documentation-compatibility correction, the complete suite reported
`820 passed in 22.63s` with `84%` total branch coverage. Python compilation and
`git diff --check` passed.

The controlled real-app recovery gate also passed: format-4 export, Clear All
Data, replacement restore, exact posted/Pending/Internal/Pass-through recovery,
counterparty preservation, exact account balances and Income/Expenses, and
relaunch persistence. The verified checkpoint was committed as `01299eb`
(`Extend recovery for pass-through transfers`).

## Task 7 Release Evidence

Task 7 raised verified progress to `100%`. The complete Windows suite reported
`824 passed in 22.65s` with `84%` total branch coverage. Python compilation and
`git diff --check` passed, and GitHub Actions on the release branch was green.

The permanent signed Android release artifact is `Enkryon-v1.3.0.apk`, size
`45,775,760 bytes`, with SHA-256
`fcb2766b02be8d344e534ae0961f2aedf0e3dbb509c3ce4106f90a19d484289c`.
`apksigner` verified the permanent Enkryon certificate SHA-256
`E3:D2:9B:10:8A:69:4A:ED:75:87:FD:99:5F:00:B0:22:64:97:B5:66:A6:53:3A:E8:47:EF:23:71:A0:12:C4:3D`,
and `zipalign -c -P 16 -v 4` passed. Android package inspection reported
`com.intian.enkryon`, version name `1.3.0`, version code `102410300`, minimum
API 24, target API 36, and both `arm64-v8a` and `armeabi-v7a` native
architectures.

Physical-device verification passed for a clean v1.3.0 install and for the
official v1.2.0-to-v1.3.0 in-place upgrade using `adb install -r`. Existing
posted and Pending records retained their exact financial effects, existing
v1.2.0 transfers remained Internal after migration 7, and a new Pass-through
exchange produced equal and opposite account outflow/inflow effects without
changing Income, Expenses, category totals, or the all-account balance.
Force-stop and relaunch preserved the migrated and new records.

The final recovery gate also passed: backup format 4 export, Clear All Data,
replacement restore, and relaunch preserved transfer kind, counterparty,
posted/Pending status, amounts, notes, dates, relationships, balances, and
totals. No unresolved critical or high-severity release defect remains.

The release is approved for merge, final main-branch CI verification, annotated
`v1.3.0` tagging, and publication. No additional feature change belongs in the
release source after this evidence checkpoint.


## Accounting Correction

The previous release approval is superseded. Publication was stopped before
merge/tag after identifying that Pass-through balances were derived from the
parent transfer row without explicit external inflow/outflow records.

The corrected candidate adds migration 8 and `pass_through_movements`. A
Pass-through parent has zero direct balance effect. A complete exact movement
pair is required before participating accounts receive a Pass-through balance
effect. Internal Transfers remain unchanged.

The previous APK evidence is historical only. The corrected source must repeat
the full Windows, CI, signed APK, clean-install, official v1.2.0 upgrade,
backup/restore, and relaunch gates before v1.3.0 is approved.


## Balance-Neutrality Correction

A later physical-device review invalidated the movement-accounting candidate.
The Pass-through record must represent the complete counterparty exchange, not
only the visible external receive/pay legs.

Controlled example:

- Bank starts at 3,000 and Cash starts at 9,000.
- The counterparty sends 1,000 into Bank.
- That 1,000 is moved from Bank to Cash.
- The counterparty receives 1,000 from Cash.
- Bank ends at 3,000 and Cash ends at 9,000.

Final invariant: a Pass-through changes neither participating account balance
and never changes Income, Expenses, category totals, or posted net cash flow.
Internal Transfer behavior remains unchanged.

Migration 8 is retained as superseded development history so databases that
already recorded it remain upgradeable. Migration 9 removes the temporary
`pass_through_movements` table, triggers, and index. The final balance query
ignores Pass-through rows completely.

All previous v1.3.0 APK hashes, clean-install results, upgrade results, and
release-approval statements are superseded. Release remains blocked until the
balance-neutral source passes the complete automated and Android gates.


## Final v1.3.0 Release Evidence

The balance-neutral correction completed the full release gate.

- Windows: `830 passed in 23.65s` at `84%` total branch coverage.
- Main-branch sanity: `830 passed in 23.32s`.
- Python compilation and `git diff --check`: passed.
- Desktop real-app Pass-through balance-neutrality check: passed.
- Corrected signed Android clean install and launch: passed.
- Official v1.2.0-to-v1.3.0 in-place upgrade: passed.
- Pass-through workflow after upgrade: both participating account balances,
  Income, and Expenses remained unchanged.
- Backup format 4 export, Clear All Data, replacement restore, and relaunch:
  passed.
- Balance-neutral correction commit: `e6cb735`.
- Main merge commit: `1a0867c45ab7922c0d304cbc47331e485319e2b6`.
- Final artifact: `Enkryon-v1.3.0.apk`.
- Artifact size: `45,776,720 bytes`.
- Artifact SHA-256: `EBEBFD56F1FFE55785E5C289D945F4C85BB8375FB81F0CF7A185142B904FBE78`.

All earlier v1.3.0 APK hashes and movement-accounting approvals remain
superseded. This final evidence is the release record for v1.3.0.
