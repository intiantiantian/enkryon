# Enkryon v1.4.0

Release date: `2026-08-09`

Release status: `RELEASE CANDIDATE`

## Summary

Enkryon 1.4 adds optional Daily Bank Interest tracking. An interest-bearing
account can store effective-dated nominal APR settings, show deterministic
non-posting daily estimates, and reconcile the bank's actual credited amount
into one normal posted Income transaction.

Estimated interest never silently creates money. Account balance, Income,
category totals, and posted financial history change only when the user
explicitly reconciles an actual bank credit.

## User-visible changes

- Added an `INTEREST` action to account cards.
- Added effective-dated APR configuration with fixed Actual/365 disclosure.
- Added today's estimate and accumulated unposted estimate views.
- Added explicit reconciliation with actual credited amount, date, Income
  category, estimated-period total, and variance.
- Added effective-dated Disable and destructive Remove Interest actions.
- Remove Interest clears interest-only configuration/accrual metadata but keeps
  already-posted bank-interest Income intact.
- Added backup format 5 so interest profiles, exact accrual state, and
  reconciliation links survive export, replacement restore, and relaunch.

## Interest calculation contract

- Rate meaning: nominal APR, not APY.
- Day-count basis: Actual/365 for v1.4.0.
- Balance basis: applicable prior end-of-day posted account balance.
- Pending Transactions: excluded.
- Internal Transfers: affect each participating account basis directionally.
- Pass-through Transfers: zero balance effect and zero interest-basis effect.
- Non-positive balances: accrue zero positive interest.
- Money/rate arithmetic: float-free; persisted amounts remain integer centavos
  with an exact rational remainder for sub-centavo carry.
- Presentation rounding: `ROUND_HALF_UP`; rounding does not rewrite exact stored
  accrual value.
- Accrual generation: idempotent by account/date.
- Actual bank credit: posted only through explicit reconciliation.

## Upgrade and stored data

- Upgrade source for final device verification: official `v1.3.0`.
- Migration 10 adds effective-dated `account_interest_profiles` and exact
  `account_interest_accruals` records.
- Migrations 1 through 9 remain unchanged released history.
- Backup format 5 preserves interest profiles/accruals alongside Pending status,
  Internal/Pass-through kind, counterparty, and all existing records.
- Backup formats 1 through 4 remain restorable and restore with empty interest
  tables because those formats never contained interest records.

## Verification completed before Android closeout

- Windows release-candidate suite: `913 passed in 31.26s`.
- Total branch coverage: `82%`.
- Python compilation: `PASSED`.
- Git whitespace check: `PASSED`.
- Desktop interest configuration/UI checks: `PASSED`.
- Desktop actual-credit reconciliation and duplicate prevention: `PASSED`.
- Desktop Remove Interest behavior: `PASSED`.
- Backup format 5 export/Clear All Data/restore/relaunch workflow: `PASSED`.

## Android release evidence

The following evidence must be replaced with observed results before publication:

- GitHub Actions: `PENDING FINAL`.
- Signed APK verification: `PENDING FINAL`.
- APK alignment: `PENDING FINAL`.
- Clean install and launch: `PENDING FINAL`.
- Official v1.3.0-to-v1.4.0 in-place upgrade: `PENDING FINAL`.
- Migration 10 / controlled Daily Bank Interest device workflow: `PENDING FINAL`.
- Backup format 5 replacement restore and relaunch: `PENDING FINAL`.

## Android compatibility

- Package: `com.intian.enkryon`
- Version name: `1.4.0`
- Version code: `PENDING FINAL BUILD VERIFICATION`
- Minimum Android API: `24`
- Target Android API: `36`
- Architectures: `arm64-v8a`, `armeabi-v7a`

## Artifact

- Filename: `Enkryon-v1.4.0.apk`
- Size: `PENDING FINAL BUILD VERIFICATION`
- SHA-256: `PENDING FINAL BUILD VERIFICATION`
- Signing certificate SHA-256: permanent Enkryon release certificate; verify
  against the release checklist before publication.

## Known limitations

- Estimates are guidance and do not claim tax or bank-statement accuracy.
- v1.4.0 uses nominal APR and Actual/365 only; bank-specific APY/360/366 rules
  are not modeled automatically.
- Automatic background posting is intentionally not supported.
- Financial data remains local unless the user exports a backup.
- Restore replaces current data; it does not merge backup and current records.
