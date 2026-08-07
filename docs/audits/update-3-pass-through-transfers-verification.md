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
| 2. Add migration and transfer-kind persistence | 18% | In progress — Windows verification pending |
| 3. Add pass-through service workflows | 17% | Not started |
| 4. Build pass-through transfer interface | 18% | Not started |
| 5. Integrate balances, activity, search, and filters | 16% | Not started |
| 6. Extend backup, recovery, and performance | 12% | Not started |
| 7. Close and release Update 3 | 10% | Not started |
| **Total** | **100%** | **9% verified** |

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
