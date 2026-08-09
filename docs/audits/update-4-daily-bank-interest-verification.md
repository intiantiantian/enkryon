# Update 4 Daily Bank Interest Verification

## Baseline

- Released source baseline: `v1.3.0`, commit `761b5d9`.
- Branch: `update-4-daily-bank-interest`.
- Python: `3.13.14` on Windows.
- Released reference: `830` tests at `84%` coverage.
- Initial branch baseline exposed two stale release-document assertions; product
  code, compilation, whitespace, and working tree were otherwise clean.

## Weighted Progress

| Task | Weight | State |
|---|---:|---|
| 1. Lock interest and rounding contract | 10% | Completed — `d867db6` |
| 2. Add profile and accrual persistence | 18% | Completed — `bd77e60` |
| 3. Build exact daily interest engine | 22% | Completed — `db2b0f3` |
| 4. Add account interest interface | 17% | Completed — `7aa1d60`, polished in `61b7b63` |
| 5. Add posting and reconciliation workflow | 13% | Completed — `d9acb4c` |
| Refinement: Remove Interest | 0% | Completed — `5f1b64e` |
| 6. Integrate history, backup, and performance | 10% | Completed — `6c618e4` |
| 7. Close and release Update 4 | 10% | In progress — Android/release evidence pending |
| **Total verified before final Android gate** | **90%** | **Release candidate** |

## Locked Financial Contract

- Nominal APR, not APY.
- Actual/365.
- Applicable prior end-of-day posted account balance.
- Pending Transactions excluded from the balance basis.
- Internal Transfers affect participating account balances normally.
- Pass-through Transfers have zero balance and zero interest-basis effect.
- Non-positive balances accrue zero positive interest.
- Exact integer/rational arithmetic preserves sub-centavo value.
- `ROUND_HALF_UP` is presentation/posting-boundary rounding only.
- Effective-dated profile history prevents silent historical rate rewrites.
- Accrual generation is idempotent by account/date.
- Estimates remain non-posting until explicit actual-credit reconciliation.

## Persistence and Recovery

Migration 10 stores effective-dated interest profiles plus exact daily accrual
rows. Accruals snapshot the relevant profile, closing posted balance, rate,
whole-centavo amount, exact remainder, status, and optional linked posted Income
transaction.

Backup format 5 preserves those records exactly. Formats 1 through 4 remain
restorable and normalize with no interest history. Clear All Data removes
interest rows in dependency order. Remove Interest deletes interest-only data
for one account while preserving any already-posted Income transaction.

## Desktop Verification

- Task 1 final contract/full gate: `835 passed`, `84%` coverage.
- Task 2 focused persistence gate: `66 passed` in the user's authoritative run.
- Task 3 focused exact-engine gate: `49 passed`.
- Task 4 interface/polish gates passed; desktop visual checks drove scroll,
  clipping, button, and account-card refinements before acceptance.
- Task 5 reconciliation plus shared-filter regression gates passed; controlled
  desktop reconciliation created one actual posted Income credit and prevented
  a duplicate period post.
- Remove Interest app checks passed; already-posted interest Income remained.
- Task 6 focused backup/performance checks passed after aligning two stale test
  assumptions with SQLite planner freedom and new Clear All Data wording.
- Final Windows pre-Android suite: `913 passed in 31.26s`, `82%` branch coverage.
- Python compilation: passed.
- Git whitespace check: passed.

## Remaining Final Release Evidence

Task 7 cannot be marked complete until all of the following are observed and
recorded:

1. Green GitHub Actions on the release-candidate branch/commit.
2. Signed/aligned `Enkryon-v1.4.0.apk` built with the permanent certificate.
3. Clean installation and launch on the supported physical Android device.
4. Official `v1.3.0` to `v1.4.0` in-place upgrade with migration 10 applied once.
5. Controlled on-device interest estimate, reconciliation, Disable/Remove, and
   old Pending/Internal/Pass-through semantic checks.
6. Backup format 5 export, Clear All Data, replacement restore, relaunch, and no
   duplicate accrual/Income evidence.
7. Final APK `versionName`, `versionCode`, size, SHA-256, and certificate
   fingerprint recorded.
8. Release records finalized, branch merged, annotated `v1.4.0` tag created, and
   GitHub release published.
