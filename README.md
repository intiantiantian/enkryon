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
Enkryon-v0.3.0.apk
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

├── assets/          # Images, icons, screenshots
├── database/        # SQLite repositories
├── kv/              # Kivy UI layouts
├── screens/         # Screen controllers
├── services/        # Business logic
├── tests/           # Automated tests
├── utils/           # Helper utilities
├── widgets/         # Reusable UI components
├── main.py
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

Repository modules separate database operations from the user interface to improve maintainability and testing.

---

## Installation

Download the latest APK from **GitHub Releases**.

Install the APK on an Android device.

> Android may require enabling installation from unknown sources because the application is not distributed through Google Play.

---

## Roadmap

### Completed

- Dashboard
- Transaction Management
- Account Management
- Category Management
- Transaction History
- Settings
- Android APK

### Planned

- Transaction search
- Advanced filters
- Reports and charts
- Budget tracking
- Import / Export
- Backup and restore
- Cloud synchronization
- Dark mode

---

## Highlights

- Built entirely with Python
- Mobile-first interface using KivyMD
- Offline-first architecture
- SQLite local database
- Repository pattern for database access
- Reusable custom UI components
- Automated tests
- Android deployment using Buildozer

---

## License

This project was developed for educational and portfolio purposes.

It is not intended for commercial use.