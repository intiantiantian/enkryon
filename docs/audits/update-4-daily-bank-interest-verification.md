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
| 7. Close and release Update 4 | 10% | Completed — verified release source finalized on `main` |
| **Total** | **100%** | **Released as v1.4.0** |

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
- Final Windows release-candidate suite: `918 passed in 31.14s`, `82%` branch coverage.
- Python compilation: passed.
- Git whitespace check: passed.

## Final Android and Release Evidence

- Release-candidate commit: `fe34913`.
- GitHub Actions: passed on the release-candidate branch.
- APK: `Enkryon-v1.4.0.apk`.
- APK size: `45,802,212` bytes.
- APK SHA-256:
  `7f58a722423eb736772534dc83832061e779a52578ec1471e7471084a2ab45e9`.
- Android package: `com.intian.enkryon`.
- Android version name: `1.4.0`.
- Android version code: `102410400`.
- Minimum API: `24`; target API: `36`.
- Native architectures: `arm64-v8a`, `armeabi-v7a`.
- `android:allowBackup=false` verified in the packaged manifest.
- APK Signature Scheme v2 verification: passed.
- Permanent signing certificate SHA-256:
  `E3:D2:9B:10:8A:69:4A:ED:75:87:FD:99:5F:00:B0:22:64:97:B5:66:A6:53:3A:E8:47:EF:23:71:A0:12:C4:3D`.
- `zipalign -c -P 16 -v 4`: passed.
- Clean installation and launch on the supported physical Android device: passed.
- Clean-install core transaction/filter/interest/persistence checks: passed.
- Official v1.3.0 (`versionCode=102410300`) to v1.4.0
  (`versionCode=102410400`) in-place upgrade with `adb install -r`: passed.
- Controlled post-upgrade Pending/Internal/Pass-through preservation checks: passed.
- Controlled Daily Bank Interest configuration and estimate-basis checks: passed.
- Actual-credit reconciliation and duplicate-prevention checks: passed.
- Backup format 5 export, Clear All Data, replacement restore, force-stop/relaunch,
  interest-profile preservation, and no-duplicate checks: passed.

## Main-Branch Closeout

- The verified Update 4 branch was fast-forward merged into `main` at `d99af7d`.
- `origin/main` was synchronized successfully.
- Post-merge release sanity gate: `16 passed`.
- Python compilation: passed.
- Git whitespace check: passed.
- Working tree after the merge sanity gate: clean.
- The source tree is finalized for the annotated `v1.4.0` tag and GitHub Release
  publication with the already-verified APK, checksum, and release notes.
