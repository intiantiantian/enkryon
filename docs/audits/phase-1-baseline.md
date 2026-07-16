# Phase 1 Baseline

## Environment

* Python: 3.13.14
* Kivy: 2.3.1
* KivyMD: 1.2.0
* Operating system: Windows 11
* Tested date: July 14, 2026

## Test Conditions

The application was tested from a clean installation state with:

* no accounts;
* no category groups;
* no categories;
* no transactions;
* no existing user data.

Testing followed the expected first-time-user workflow:

1. Launch the application.
2. Inspect all empty states.
3. Create an account.
4. Create income and expense category groups.
5. Create income and expense categories.
6. Create income and expense transactions.
7. Edit and delete transactions.
8. Rename accounts and categories.
9. Test data relationships.
10. Restart the application and verify persistence.
11. Clear all application data.

## Working Features

### Application

* [x] Launch application with a clean database
* [x] Display zero balances on first launch
* [x] Navigate between existing screens
* [x] Preserve data after restarting the application
* [x] Clear all application data
* [x] Cancel the Clear Data confirmation

### Accounts

* [x] Create account
* [x] Reject empty account name
* [x] Reject duplicate account name
* [x] Rename account
* [x] Delete unused account
* [x] Refresh renamed account across all screens
* [x] Protect accounts referenced by transactions

### Categories

* [x] Create income category group
* [x] Create expense category group
* [x] Create income category
* [x] Create expense category
* [x] Rename category group
* [x] Rename category
* [x] Expand and collapse category groups
* [x] Reject empty category and group names
* [x] Validate duplicate category and group names consistently
* [x] Protect categories referenced by transactions

### Transactions

* [x] Add income
* [x] Add expense
* [x] Edit transaction
* [x] Change transaction type while editing
* [x] Delete transaction
* [x] Recalculate account balance
* [x] Recalculate income and expense totals
* [x] Display transactions in transaction history
* [x] Preserve transactions after application restart
* [x] Validate missing amount
* [x] Validate zero amount
* [x] Validate missing account
* [x] Validate missing category
* [x] Prevent multiple decimal points
* [x] Support keypad delete and clear actions
* [x] Handle excessively large monetary values safely
* [x] Support all planned transaction filters

### Filters

* [x] Display all transactions
* [x] Filter income transactions
* [x] Filter expense transactions
* [x] Filter transactions by account
* [ ] Filter transactions by category
* [ ] Filter transactions by date
* [ ] Reset all filters
* [x] Display an empty state when filters return no results

## Known Defects

### DEF-001 — Referenced account deletion

Screen: Accounts  
Status: Fixed in Phase 1.1  

Steps tested:
1. Created an account.
2. Added a transaction using that account.
3. Attempted to delete the account.

Expected:
The app should prevent deletion because transactions reference the account.

Actual after fix:
The account was not deleted. The app showed a warning message.

Result:
Passed.

---

### DEF-002 — Referenced category deletion

Screen: Categories  
Status: Fixed in Phase 1.1  

Steps tested:
1. Created a category.
2. Added a transaction using that category.
3. Attempted to delete the category.

Expected:
The app should prevent deletion because transactions reference the category.

Actual after fix:
The category was not deleted. The app showed a warning message.

Result:
Passed.

---

### DEF-003 — Large monetary values break dashboard layout

Screen: Dashboard / Transaction rows  
Status: Fixed in Phase 1.1  

Steps tested:
1. Added transactions with very large amounts.
2. Returned to the dashboard.
3. Checked current balance, income, expense, and transaction rows.

Expected:
Large monetary values should remain readable and should not break the layout.

Actual after fix:
Large values are displayed using compact formatting. Labels remain within their containers.

Result:
Passed.

---

### DEF-004 — Dashboard does not refresh after account/category changes

Screen: Dashboard  
Status: Fixed in Phase 1.1  

Steps tested:
1. Selected an account on the dashboard.
2. Renamed the selected account.
3. Returned to the dashboard.
4. Renamed a category used by a recent transaction.
5. Returned to the dashboard.

Expected:
Dashboard should show the latest account name, latest transaction labels, and updated totals.

Actual after fix:
Dashboard refreshed on entry. The selected account label, balance, totals, and recent transactions updated correctly.

Result:
Passed.

---

### DEF-005 — Inconsistent duplicate category validation

Screen: Categories  
Status: Fixed in Phase 1.1  

Business rule:
- Category group names must be unique per transaction type.
- Category names must be unique per transaction type.
- Income and expense may use the same category name.
- Validation ignores leading/trailing spaces and capitalization.

Steps tested:
1. Tried creating duplicate group names with different capitalization.
2. Tried creating duplicate category names with different capitalization.
3. Tried creating the same category name under Income and Expense.

Expected:
Duplicates within the same transaction type should be blocked. The same name across Income and Expense should be allowed.

Actual after fix:
The app blocked same-type duplicates and allowed cross-type names.

Result:
Passed.

---

### DEF-006 — Empty lists show blank areas

Screen: Dashboard / Transactions / Accounts / Categories  
Status: Fixed in Phase 1.1  

Steps tested:
1. Cleared application data.
2. Opened Dashboard recent transactions.
3. Opened Transactions.
4. Opened Accounts.
5. Opened Categories for Income and Expense.
6. Created an empty category group and expanded it.
7. Added records and confirmed the empty states disappeared.

Expected:
Empty areas should show helpful messages instead of blank space.

Actual after fix:
Dashboard, Transactions, Accounts, Category Groups, and empty Category Group contents displayed reusable empty-state UI messages.

Result:
Passed.

## Visual Inconsistencies

### Branding

* The app icon colors do not match the colors used inside the application.
* The splash screen colors do not match the current app interface.
* The icon uses a dark emerald and gold visual identity, while the app mainly uses pale and medium greens.
* Gold from the icon is not consistently used as an accent inside the application.

### Buttons

* Dialog buttons use a different green from the primary buttons used on screens.
* Management buttons for accounts and categories appear too tightly fitted.
* Button sizes and internal padding require further review.
* Empty-state screens do not consistently provide a clear action button.

### Cards

* Card padding is not consistent across all screens.
* Text alignment varies between similar cards.
* Large monetary values can overflow card boundaries.

### Typography

* Screen titles do not use a fully consistent typography style.
* Section titles do not use a fully consistent typography style.
* Body text does not use a fully consistent typography style.
* Monetary values do not follow a consistent hierarchy.
* Large values are not displayed responsively.

### Colors

* Income and expense values are not sufficiently distinguishable in every context.
* Dialog components introduce a green that is inconsistent with the main interface.
* The application does not yet use a centralized semantic color system.

### Empty States

* The Dashboard empty state is understandable.
* The Accounts empty state is understandable.
* The Categories empty state is understandable.
* The Transactions screen does not display an appropriate empty state.
* Empty states do not consistently provide a clear next action.

### Layout

* Large monetary values can overlap or overflow nearby components.
* Long text has not yet been fully tested across all screens.
* Some buttons appear too small or tightly fitted for their labels.
* Layouts rely on fixed dimensions that may not support unusual content.
* Scrollable content remains accessible during normal testing.

## Skipped or Blocked Tests

The following tests were skipped or blocked because the required features are not yet implemented:

* category transaction filtering;
* date transaction filtering;
* filter reset behavior;
* some filtered empty-result scenarios.

These are classified as missing functionality rather than defects in an implemented feature.

## Test Summary

* Total test cases: 29
* Passed: 21
* Failed: 7
* Blocked: 1
* Not supported: 0

## Defect Summary

* Critical defects: 2
* High-severity defects: 1
* Medium-severity defects: 2
* Low-severity defects: 1

The failed tests BL-018 and BL-023 are represented by the same underlying large-value layout defect.

## Baseline Decision

* [ ] Stable enough to begin full visual refactoring
* [x] Functional defects must be corrected first
* [x] Database integrity issues must be corrected first
* [ ] Additional baseline testing is required

## Recommended Repair Order

1. Prevent deletion of accounts referenced by transactions.
2. Prevent deletion of categories referenced by transactions.
3. Add defensive handling for existing orphaned transaction data.
4. Correct large-value monetary layouts.
5. Refresh account data after account creation, rename, and deletion.
6. Correct duplicate category and group validation.
7. Add a Transactions empty-state message.
8. Complete the remaining transaction filters later in the feature roadmap.

## Conclusion

Enkryon’s primary account, category, and transaction workflows are functional. Users can create, edit, delete, and persist financial records under normal conditions.

However, the application currently allows accounts and categories to be deleted while they are still referenced by transactions. This creates orphaned records and can cause the application to crash when those transactions are edited. These database integrity defects must be corrected before the main visual and architectural refactoring begins.

After the critical and high-severity defects are fixed and retested, the application will be ready to proceed with the broader Phase 1 theme, design-system, and code-quality improvements.
