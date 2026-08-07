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
| 5. Integrate balances, activity, search, and filters | 16% | In progress — verification pending |
| 6. Extend backup, recovery, and performance | 12% | Not started |
| 7. Close and release Update 3 | 10% | Not started |
| **Total** | **100%** | **62% verified** |

## Task 1 Contract Decisions

- Canonical exchange: friend deposits to Bank while the user gives equivalent
  Cash; record the user-owned balance direction as `Cash → Bank`.
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
shows directional guidance that locks the canonical `Cash → Bank` cash-out
example and explicitly states that principal is not Income or Expense.

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
text and `Pass-through Transfer`, preserve `Cash to Bank` direction wording, and
show `Counterparty: <name>` when present. Because Dashboard recent activity uses
the same activity/card path, the same non-color-only Pass-through treatment is
shown there without adding extra Dashboard filter controls. Recycled transaction
cards explicitly clear transfer-kind/counterparty state.

The Task 4 cash-out guidance also changes the UI example from `Cash → Bank` to
`Cash to Bank`. Documentation may retain mathematical or directional symbols,
but user-facing Kivy copy should prefer plain ASCII wording when the symbol is
not necessary.

No transfer-kind index is added in Task 5. Task 6 remains responsible for the
large-history/query-plan gate and may add an index only if measured plans justify
it.
