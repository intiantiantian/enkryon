from database.account_repository import delete_account, insert_account
from database.category_group_repository import insert_category_group
from database.category_repository import delete_category, insert_category
from database.transaction_repository import (
    delete_transaction,
    get_current_balance_centavos,
    get_total_centavos,
    get_transaction_by_id,
    get_transactions,
    insert_transaction,
    update_transaction,
)


def create_transaction_test_data():
    insert_account("Cash")
    insert_account("Savings")

    insert_category_group("Salary", "income")
    insert_category_group("Food", "expense")

    insert_category(1, "Paycheck")
    insert_category(2, "Lunch")


def test_insert_transaction_and_get_by_id():
    create_transaction_test_data()

    insert_transaction(
        account_id=1,
        amount_centavos=1000,
        category_id=1,
        date_time="2026-07-15 08:00:00",
        notes="Allowance",
    )

    transaction = get_transaction_by_id(1)

    assert transaction == (
        1,
        1,
        1000.0,
        1,
        "2026-07-15 08:00:00",
        "Allowance",
        "Cash",
        "Paycheck",
        1,
        "Salary",
        "income",
    )


def test_get_transactions_orders_latest_first():
    create_transaction_test_data()

    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Morning")
    insert_transaction(1, 200, 2, "2026-07-15 10:00:00", "Lunch")
    insert_transaction(1, 500, 1, "2026-07-15 09:00:00", "Bonus")

    transactions = get_transactions()

    assert [transaction[0] for transaction in transactions] == [2, 3, 1]


def test_get_transactions_can_filter_by_account():
    create_transaction_test_data()

    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Cash income")
    insert_transaction(2, 500, 1, "2026-07-15 09:00:00", "Savings income")

    transactions = get_transactions(account_id=2)

    assert len(transactions) == 1
    assert transactions[0][1] == "Savings"
    assert transactions[0][4] == 500.0


def test_get_transactions_can_filter_by_transaction_type():
    create_transaction_test_data()

    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Income")
    insert_transaction(1, 200, 2, "2026-07-15 09:00:00", "Expense")

    income_transactions = get_transactions(transaction_type="income")
    expense_transactions = get_transactions(transaction_type="expense")

    assert len(income_transactions) == 1
    assert income_transactions[0][7] == "income"

    assert len(expense_transactions) == 1
    assert expense_transactions[0][7] == "expense"


def test_get_transactions_can_limit_results():
    create_transaction_test_data()

    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "First")
    insert_transaction(1, 500, 1, "2026-07-15 09:00:00", "Second")
    insert_transaction(1, 200, 2, "2026-07-15 10:00:00", "Third")

    transactions = get_transactions(limit=2)

    assert len(transactions) == 2
    assert [transaction[0] for transaction in transactions] == [3, 2]


def test_update_transaction():
    create_transaction_test_data()
    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Original")

    result = update_transaction(
        account_id=2,
        amount_centavos=750,
        category_id=2,
        date_time="2026-07-15 12:30:00",
        notes="Updated",
        transaction_id=1,
    )

    transaction = get_transaction_by_id(1)

    assert result is True
    assert transaction == (
        1,
        2,
        750.0,
        2,
        "2026-07-15 12:30:00",
        "Updated",
        "Savings",
        "Lunch",
        2,
        "Food",
        "expense",
    )


def test_delete_transaction():
    create_transaction_test_data()
    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Income")

    result = delete_transaction(1)

    assert result is True
    assert get_transactions() == []


def test_get_total_centavos_by_type():
    create_transaction_test_data()

    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Income 1")
    insert_transaction(1, 500, 1, "2026-07-15 09:00:00", "Income 2")
    insert_transaction(1, 200, 2, "2026-07-15 10:00:00", "Expense")

    assert get_total_centavos("income") == 1500.0
    assert get_total_centavos("expense") == 200.0


def test_get_total_centavos_can_filter_by_account():
    create_transaction_test_data()

    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Cash income")
    insert_transaction(2, 500, 1, "2026-07-15 09:00:00", "Savings income")
    insert_transaction(1, 200, 2, "2026-07-15 10:00:00", "Cash expense")

    assert get_total_centavos("income", account_id=1) == 1000.0
    assert get_total_centavos("income", account_id=2) == 500.0
    assert get_total_centavos("expense", account_id=1) == 200.0


def test_get_current_balance_centavos():
    create_transaction_test_data()

    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Income")
    insert_transaction(1, 250, 2, "2026-07-15 09:00:00", "Expense")

    assert get_current_balance_centavos() == 750.0


def test_get_current_balance_centavos_can_filter_by_account():
    create_transaction_test_data()

    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Cash income")
    insert_transaction(1, 250, 2, "2026-07-15 09:00:00", "Cash expense")
    insert_transaction(2, 500, 1, "2026-07-15 10:00:00", "Savings income")

    assert get_current_balance_centavos(account_id=1) == 750.0
    assert get_current_balance_centavos(account_id=2) == 500.0


def test_referenced_account_cannot_be_deleted():
    create_transaction_test_data()
    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Income")

    result, reason = delete_account(1)

    assert result is False
    assert reason == "referenced"


def test_referenced_category_cannot_be_deleted():
    create_transaction_test_data()
    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Income")

    result, reason = delete_category(1)

    assert result is False
    assert reason == "referenced"