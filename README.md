# Enkryon

A modern **offline-first personal finance tracker** built with **Python**, **Kivy**, **KivyMD**, and **SQLite**.

Enkryon is an offline-first personal finance tracker that helps users record income and expenses, organize accounts and categories, and monitor their financial activity through a clean and intuitive interface.

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

---

## Features

### Dashboard

- View current balance
- View total income
- View total expenses
- Filter dashboard by account
- Quick access to common actions

### Transactions

- Add income transactions
- Add expense transactions
- Edit transactions
- Delete transactions
- Custom numeric keypad
- Select account
- Select category group
- Select category
- Add notes
- Date and time selection

### Accounts

- Create accounts
- Rename accounts
- Delete accounts
- Duplicate name validation

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

- View all transactions
- Filter by transaction type
- Edit transactions
- Delete transactions

### Settings

- Clear all application data

---

## Download

The latest Android APK is available from the GitHub Releases page.

Latest release:

```
Enkryon-v0.4.8.apk
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

Transaction amounts are stored as exact integer centavos. Ordered database
migrations safely upgrade older installations while preserving records,
relationships, transaction IDs, and totals.

Repository modules separate database operations from the user interface to
improve maintainability and testing. See the
[database architecture guide](docs/development/database.md) for details.

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
- Phase 5 is next and focuses on simplifying screen and business logic.
- Later phases cover usability, recovery, search, and version 1.0
  validation before major feature expansion.

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

---

## License

This project was developed for educational and portfolio purposes.

It is not intended for commercial use.
