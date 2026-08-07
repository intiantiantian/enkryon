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
| 1. Lock pass-through contract and baseline | 9% | In progress — baseline verified; contract gate pending |
| 2. Add migration and transfer-kind persistence | 18% | Not started |
| 3. Add pass-through service workflows | 17% | Not started |
| 4. Build pass-through transfer interface | 18% | Not started |
| 5. Integrate balances, activity, search, and filters | 16% | Not started |
| 6. Extend backup, recovery, and performance | 12% | Not started |
| 7. Close and release Update 3 | 10% | Not started |
| **Total** | **100%** | **0% verified until Task 1 gate passes** |

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

Task 1 changes documentation and contract tests only. Migration 7, repository,
service, UI, activity, and backup-format implementation must not begin until the
contract checkpoint passes and is committed.
