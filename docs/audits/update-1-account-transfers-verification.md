# Update 1 Account Transfers Verification

## Status

Release-candidate preparation is in progress. Checkpoints 1-6 are verified and
committed; the final 10% release gate remains pending.

## Verified Checkpoints

| Checkpoint | Weight | Commit | Verified result |
|---|---:|---|---|
| Contract and baseline | 6% | `02f0161` | Transfer invariants, v1.0.0 baseline, branch, and clean start recorded. |
| Migration and persistence | 19% | `bb60e7e` | Migration 5, constraints, indexes, atomic CRUD, ordering, and legacy upgrade passed. |
| Form state and services | 16% | `10275b7` | Exact validation plus create/edit/delete/restore workflows passed. |
| Transfer interface | 18% | `54efeb1` | Navigation, selectors, inputs, responsive layout, enlarged fonts, and app checks passed. |
| Balances and activity | 20% | `7b56666` | Direction-aware balances, net-zero invariants, unified history, filters, actions, and large-history regressions passed. |
| Backup and account safety | 11% | `8d95422` | Backup format 2, format-1 compatibility, restore/Clear All Data rollback, and referenced-account protection passed. |

Verified weighted progress: `90%`.

## Proven Invariants

- One transfer is stored and mutated as one atomic database record.
- Source and destination accounts exist and differ.
- Amounts remain positive integer centavos from form state through storage and
  balance calculations.
- Outgoing transfers reduce one account and incoming transfers increase the
  other by the exact amount.
- The all-accounts balance, Income, Expenses, and category totals do not change
  because of transfers.
- Unified activity ordering is stable across transaction and transfer IDs.
- Transfer search and filters cover notes, either account, activity type, and
  inclusive dates.
- Transfer-referenced accounts cannot be deleted.
- Format-2 backup recovery preserves transfers, IDs, sequences, counts, and
  relationships; late failures roll back the complete replacement.
- Compatible format-1 v1.0 backups restore with an empty transfer collection.

## Final Release Gate

The remaining 10% requires all of the following evidence:

1. Complete Windows suite with coverage passes after the v1.1.0 identity and
   documentation changes.
2. Python compilation and Git whitespace checks pass.
3. The release-candidate branch is pushed and GitHub Actions is green.
4. The signed `Enkryon-v1.1.0.apk` passes package, API, ABI, content,
   permanent-certificate, alignment, size, and checksum checks.
5. A clean installation passes the core transfer and recovery smoke tests.
6. Official `v1.0.0` upgrades in place through migration 5 without losing or
   changing controlled records.
7. A post-upgrade transfer, relaunch, backup, clear, and restore cycle preserves
   exact balances and transfer data.
8. No unresolved critical or high-severity defect remains.
9. Pending evidence fields in the v1.1.0 release notes and this report are
   finalized before publication and tagging.

Update 1 must remain at `90%` until the complete gate passes.
