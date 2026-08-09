# Daily Bank Interest Contract

## Scope

Update 4 (`v1.4.0`) adds optional estimated daily interest for user-selected
bank accounts and an explicit reconciliation workflow for interest actually
credited by the bank. Estimates are informational derived records. They never
create money, Income, category totals, or account-balance effects by themselves.

This document records the Task 1 financial contract that was locked before
implementation began. Migration 10 and persistence were added in Task 2, and
the exact calculation engine was added in Task 3. User-interface,
reconciliation-posting, backup-format-5, and release work remain later tasks.

## Rate meaning and storage

- The v1.4.0 rate is a nominal annual percentage rate (**APR**), not APY.
- The user enters a percentage rate with up to six decimal places.
- The persisted rate is an integer `annual_rate_micros`, where one unit is one
  millionth of one percentage point.
- Therefore `3.65%` is stored as `3_650_000` and the decimal annual rate is
  `annual_rate_micros / 100_000_000`.
- Binary floating-point arithmetic is forbidden for financial calculations.
- A disabled profile generates no new estimates. A zero APR is valid and
  generates zero accrual.

## Day-count method

v1.4.0 supports **Actual/365** only.

- Every calendar accrual date uses a denominator of 365, including February 29.
- The first release does not switch automatically to 366 in leap years.
- Other bank-specific bases such as 360 or Actual/Actual are outside v1.4.0 and
  must not be presented as supported.

## Balance basis and timing

For accrual date `D`, Enkryon uses the account's posted closing balance at the
end of calendar date `D - 1` as the balance basis.

The balance basis follows released ledger semantics:

- posted Income and Expense transactions affect the balance normally;
- Internal Transfers affect each participating account directionally;
- Pending Transactions are excluded because they are non-posting;
- Pass-through Transfers contribute zero because they are balance-neutral; and
- unreconciled interest estimates are excluded because estimates are
  non-posting.

A posted interest reconciliation is an ordinary posted Income transaction. Once
posted, that transaction affects later closing balances under the normal ledger
rules.

Zero or negative closing balances accrue zero positive interest.

## Exact accrual arithmetic

For a positive eligible closing balance:

```text
numerator = closing_balance_centavos * annual_rate_micros
denominator = 100_000_000 * 365
exact_daily_interest_centavos = numerator / denominator
```

The service performs the multiplication with exact integer arithmetic and then
uses integer division to split each accrual into:

```text
whole_centavos, remainder = divmod(numerator, 36_500_000_000)
```

`remainder` is an exact rational remainder with the fixed denominator
`36_500_000_000`; it is not a rounded decimal approximation. Persistence added
in Task 2 must preserve enough information to reconstruct this exact value.
This split also avoids requiring the potentially large multiplication result to
fit in a SQLite integer column.

Sub-centavo value is never rounded away during daily generation or accumulation.
When multiple estimates are summarized, whole-centavo and remainder components
are summed exactly before any display rounding.

## Rounding and presentation

- Stored and service-level accrual arithmetic remains exact.
- User-facing peso/centavo estimates round to the nearest centavo using
  **ROUND_HALF_UP** only at a presentation boundary.
- A displayed accumulated estimate is rounded once from the exact accumulated
  value; it is not the sum of already-rounded daily labels.
- Consequently, several days that each display as `₱0.00` may correctly produce
  an accumulated display of `₱0.01` after sub-centavo carry becomes large enough.
- Actual bank credits are never derived by rounding the estimate; the user
  enters the bank's actual credited amount in exact centavos during
  reconciliation.

## Effective-dated rate changes

Rate changes are effective-dated.

- The rate applicable to accrual date `D` is the latest enabled rate whose
  effective date is on or before `D`.
- A new rate change must not overwrite an earlier rate record.
- Each generated accrual snapshots the rate used for that date.
- Changing today's or a future rate must not silently rewrite reconciled
  historical estimates.
- Task 2 persistence must retain enough rate history to deterministically
  generate missed dates across rate changes.

## Missed dates and idempotency

Estimated accrual generation is deterministic and idempotent.

- Reopening, refreshing, or revisiting an account cannot create a second accrual
  for the same account and accrual date.
- If the app was not opened for one or more eligible dates, the service may
  generate the missing non-posting estimates from exact ledger and rate history.
- Generation never creates a posted transaction.
- Reconciled accruals are historical evidence and are not silently regenerated
  as different values.

## Reconciliation contract

A bank credit becomes financially effective only through explicit user
confirmation.

The user confirms:

- the actual credited amount in integer centavos;
- the bank credit date; and
- an existing Income category.

A successful reconciliation atomically:

1. creates exactly one normal posted Income transaction for the confirmed
   amount and date;
2. links the covered estimate period to that posted transaction;
3. marks the covered estimates reconciled; and
4. exposes the variance between the exact accumulated estimate and the actual
   credited amount as informational context.

The estimate is never silently substituted for the bank's actual amount. A
variance does not create an automatic adjustment transaction. Cancellation,
validation failure, database failure, or a repeated reconciliation attempt must
leave financial results unchanged and cannot produce duplicate Income.

## Controlled reference cases

### Case 1 - exact one-peso daily accrual

- Prior closing balance: `₱10,000.00` = `1,000,000` centavos.
- APR: `3.65%` = `3,650,000` rate micros.
- Numerator: `3,650,000,000,000`.
- Denominator: `36,500,000,000`.
- Exact daily accrual: `100` centavos = `₱1.00`.

### Case 2 - sub-centavo carry

- Prior closing balance: `₱100.00` = `10,000` centavos.
- APR: `1.00%` = `1,000,000` rate micros.
- Daily exact accrual: `10,000,000,000 / 36,500,000,000` centavos.
- Each individual day displays `₱0.00` after presentation rounding.
- Four equal days total `40,000,000,000 / 36,500,000,000` centavos, which is
  about `1.09589` centavos and displays as `₱0.01` when the exact total is
  rounded once.

### Case 3 - ledger-status and transfer semantics

Assume Bank A closes at `₱10,000.00`. On the next ledger day:

- a `₱1,000.00` posted Expense lowers its closing balance normally;
- a `₱2,000.00` Pending Expense changes neither the closing balance nor the next
  interest basis;
- a `₱3,000.00` Internal Transfer out lowers Bank A and raises its destination
  by the exact directional amounts; and
- a `₱4,000.00` Pass-through record changes neither participating account
  balance and therefore changes neither account's interest basis.

The following accrual date uses those resulting prior end-of-day posted balances.

### Case 4 - zero, negative, and leap-day behavior

- A zero prior closing balance accrues zero.
- A negative prior closing balance accrues zero positive interest.
- February 29 is an eligible calendar accrual date and still uses denominator
  365 under Actual/365.

### Case 5 - actual credit differs from estimate

If the exact accumulated estimate displays `₱12.34` but the bank actually
credits `₱12.31`, reconciliation posts exactly `₱12.31` as Income. The
`₱0.03` display variance is informational only and does not create another
transaction.

## Persistence and recovery direction

Task 2 implemented migration **10** with effective-dated APR profile history
and exact daily accrual snapshots. Task 3 uses those records without creating
posting effects. The planned backup format **5** remains intentionally deferred until
the interest records and reconciliation workflow are finalized; restore
compatibility for existing formats 1 through 4 remains required.

## Out of scope for v1.4.0

- APY-based estimation;
- bank-specific compounding formulas;
- Actual/360, 30/360, or Actual/Actual day-count methods;
- tax-accurate claims or automatic withholding-tax calculations;
- automatic background posting of interest;
- silently creating an Income transaction because a date elapsed; and
- silently altering a reconciled historical credit when estimates change.

## Task 4 account interface

Task 4 exposes interest configuration from each Account card without adding a
second account-management navigation hierarchy.

- Every account shows an explicit textual interest status.
- The interest overlay supports APR entry with up to six decimal places,
  effective-date entry in `YYYY-MM-DD`, and effective-dated disabling.
- `Actual/365` is displayed as a fixed v1.4.0 rule rather than an editable bank
  setting.
- The overlay shows today's rounded estimate and the accumulated unreconciled
  estimate while retaining exact arithmetic underneath.
- The interface labels estimates as **non-posting** and explains that they do
  not alter account balances or Income until an actual bank credit is
  reconciled.
- Saving or disabling adds a new effective-dated profile row; it never rewrites
  prior profile history.
- Revisiting the Accounts screen may idempotently generate missing estimate
  rows through the current date, but it cannot create a posted transaction.
- Disabling interest stops future estimate generation from the selected date
  while preserving previously accumulated unreconciled estimates for display.
- The interest overlay follows the global overlay Back behavior, so Android Back
  dismisses it before leaving the Accounts screen.
