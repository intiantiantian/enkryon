# Enkryon

A modern **offline-first personal finance tracker** built with **Python**, **Kivy**, **KivyMD**, and **SQLite**.

Enkryon is an offline-first personal finance tracker that helps users record
income and expenses, hold planned activity as Pending until it is posted,
move funds between accounts, record linked Pass-through exchanges, estimate
daily bank interest, reconcile actual bank credits, organize accounts and
categories, and monitor financial activity through a clean and intuitive
interface.

The application focuses on simplicity, local data privacy, and responsive mobile design.

---

## Screenshots

### Dashboard

![Dashboard](assets/screenshots/dashboard/dashboard.jpg)

### Add Transaction

![Add Transaction](assets/screenshots/transactions/add_transaction.jpg)

### Transaction History

![Transaction History](assets/screenshots/transactions/transaction_history.jpg)

### Accounts

![Accounts](assets/screenshots/accounts/accounts_populated.jpg)

### Categories

![Categories](assets/screenshots/categories/categories_populated.jpg)

### Settings

![Settings](assets/screenshots/settings/settings.jpg)

---

## Features

### Dashboard

- View current balance
- View total income
- View total expenses
- Filter dashboard by account and activity type, including Pending
- Review Pending activity without changing posted totals
- Quick access to common actions

### Transactions

- Add income transactions
- Add expense transactions
- Save income or expense transactions as Pending
- Post Pending transactions when they become financially effective
- Edit transactions
- Delete transactions
- Custom numeric keypad
- Select account
- Select category group
- Select category
- Add notes
- Date and time selection

### Account Transfers

- Move an exact amount of your own money between two accounts with Internal Transfers
- Record Pass-through exchanges without changing either participating account balance
- Keep Internal and Pass-through principal out of Income and Expenses
- Add an optional counterparty to Pass-through activity
- Edit, delete, and undo deleted transfers
- Search and filter transfer activity by account, date, notes, kind, and counterparty

### Accounts

- Create accounts
- Rename accounts
- Delete accounts
- Duplicate name validation
- Configure optional Daily Bank Interest with effective-dated APR history
- View non-posting daily and accumulated interest estimates
- Reconcile an actual bank interest credit as one posted Income transaction
- Disable interest prospectively or remove interest-only tracking data without
  deleting already-posted Income

### Categories

- Separate income and expense categories
- Category groups
- Nested categories
- Expand / collapse category groups
- Rename category groups
- Rename categories
- Delete category groups
- Delete categories
- Duplicate name validation

### Transaction History

- View transactions and account transfers newest-first
- Search notes, accounts, category groups, categories, and transfer accounts
- Filter by transaction type, account, category group, and category
- Filter transfer activity separately from income and expenses
- Filter Pending activity separately from posted income and expenses
- Filter by an inclusive date range
- Combine search and filters
- Review active filters and reset them together
- Edit transactions
- Delete transactions

### Settings

- Export backup format 5 with transfer kind, counterparty, Pending status, and
  Daily Bank Interest profiles/accruals
- Preview and restore a validated backup
- Restore formats 1 through 4 with older backups normalized safely and no
  synthetic interest history
- Clear all application data
- Export a backup before clearing data
- View application, local-data, and privacy information

---

## Download

Official Android APKs are published on the GitHub Releases page after their
release checks pass.

The verified version 1.2 Android release uses this artifact name:

```
Enkryon-v1.2.0.apk
```

The verified version 1.3 Android release uses:

```
Enkryon-v1.3.0.apk
```

The version 1.4 release candidate uses this artifact name after the final
Android release checks pass:

```
Enkryon-v1.4.0.apk
```

---

## Technologies

- Python 3.13
- Kivy 2.3.1
- KivyMD 1.2.0
- SQLite

---

## Project Structure

```
enkryon/

├── .github/         # Automated GitHub quality checks
├── assets/          # Images, icons, screenshots
├── database/        # SQLite repositories
├── docs/            # Audit and development documentation
├── kv/              # Kivy UI layouts
├── screens/         # Screen controllers
├── services/        # Business logic
├── tests/           # Automated tests
├── theme/           # Shared design values and app theme
├── utils/           # Helper utilities
├── widgets/         # Reusable UI components
├── LICENSE
├── main.py
├── ROADMAP.md
├── requirements-dev.txt
├── requirements.txt
└── README.md
```

---

## Database

Enkryon uses **SQLite** for local data persistence.

Stored data includes:

- Accounts
- Category Groups
- Categories
- Transactions
- Account transfers

Transaction and transfer amounts are stored as exact integer centavos. Ordered database
migrations safely upgrade older installations while preserving records,
relationships, transaction and transfer IDs, and totals.

Repository modules separate database operations from the user interface to
improve maintainability and testing. See the
[database architecture guide](docs/development/database.md) for details.

Named records carry database results across layer boundaries. Managed
connections protect commits, rollbacks, and cleanup, while account,
category, transaction, transfer, and unified-activity services own workflow
rules and return explicit, testable results to the interface.

User-created backups are stored as versioned JSON documents. Backup format 5
preserves each transaction's posted or Pending status, transfer kind and
counterparty metadata, and Daily Bank Interest profiles/accruals including
reconciliation links. Compatible formats 1 through 4 remain restorable; older
formats normalize missing posting, transfer, or interest fields without
inventing financial effects.
Enkryon validates the complete backup, shows its metadata and record counts,
and requires explicit confirmation before replacing current data inside a
database transaction.

On Android, the system document picker lets users choose where to save or
open a backup without granting broad storage permission. Android automatic
cloud backup remains disabled.

---

## Development and Quality Checks

Install the reproducible development environment:

```bat
python -m pip install -r requirements-dev.txt
```

Run the full suite with coverage:

```bat
python -m pytest -q --cov --cov-report=term-missing
```

GitHub Actions installs the same dependencies, compiles the Python source,
and runs the complete test suite with coverage on every push and pull
request.

See the [local testing guide](docs/development/testing.md) for the verified
environment and all required commands.

---

## Installation

Download the latest APK from **GitHub Releases**.

Install the APK on an Android device.

> Android may require enabling installation from unknown sources because the application is not distributed through Google Play.

---

## Roadmap

Development follows a reliability-first sequence:

- Phase 1 established the safe architecture and design foundation.
- Phase 2 delivered exact centavo storage and safe database migrations.
- Phase 3 established reproducible local and automatic quality checks.
- Phase 4 established repeatable, permanently signed Android releases and
  proved an in-place upgrade from official `v0.4.0` to `v0.4.8` without
  data loss.
- Phase 5 simplified the architecture with named records, managed database
  connections, explicit transaction form state, workflow services, and
  shared screen-action helpers.
- Phase 6 improved existing workflows with preserved transaction form state,
  responsive layouts, clearer navigation, actionable empty states, and
  consistent customized overlays.
- Phase 7 added versioned backup export, complete validation, confirmed
  transactional restore, Android document selection, and backup-before-clear
  recovery.
- Phase 8 added transaction search, combined advanced filters, active-filter
  summaries, clear no-results recovery, and indexed large-history queries.
- Phase 9 verified clean installation, legacy upgrades, backup and recovery,
  10,000-record histories, responsive layouts, enlarged fonts, accessibility,
  and the signed version 1.0 release.
- Update 1 adds first-class account transfers for version 1.1.0.
- Update 2 will add statistical visualizations after the transfer release is
  stable.

See the [complete development roadmap](ROADMAP.md) for objectives,
deliverables, priorities, and completion gates.

---

## Highlights

- Built entirely with Python
- Mobile-first interface using KivyMD
- Offline-first architecture
- SQLite local database
- Exact integer-centavo calculations
- Versioned, transactional database migrations
- Repository pattern for database access
- Reusable custom UI components
- Automated tests with coverage reporting
- GitHub Actions quality checks
- Android deployment using Buildozer
- Versioned, validated user-controlled backups
- Transactional replacement restore with rollback protection
- Combined transaction search and advanced filters
- Atomic account transfers with exact per-account balance effects
- Unified transaction and transfer activity history
- Indexed newest-first transaction history
- Virtualized large-history rendering

---

## License

Copyright (c) 2026 Christian Jay Villaria. All rights reserved.

The source code and repository materials are available only for viewing and
portfolio evaluation. No permission is granted to copy, modify, distribute,
or reuse them in another project. Public repository hosting terms may still
permit platform-level viewing and forking.

See [LICENSE](LICENSE) for the complete terms.
