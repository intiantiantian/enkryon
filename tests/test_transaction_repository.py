from datetime import date

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
    restore_transaction,
)
from database.records import TransactionDetailRecord, TransactionListRecord


def create_transaction_test_data():
    insert_account("Cash")
    insert_account("Savings")

    insert_category_group("Salary", "income")
    insert_category_group("Food", "expense")

    insert_category(1, "Paycheck")
    insert_category(2, "Lunch")


def test_insert_transaction_and_get_by_id():
    create_transaction_test_data()

    result = insert_transaction(
        account_id=1,
        amount_centavos=1000,
        category_id=1,
        date_time="2026-07-15 08:00:00",
        notes="Allowance",
    )

    transaction = get_transaction_by_id(1)

    assert result is True
    assert isinstance(transaction, TransactionDetailRecord)
    assert transaction == TransactionDetailRecord(
        transaction_id=1,
        account_id=1,
        amount_centavos=1000,
        category_id=1,
        date_time="2026-07-15 08:00:00",
        notes="Allowance",
        account_name="Cash",
        category_name="Paycheck",
        group_id=1,
        group_name="Salary",
        transaction_type="income",
    )


def test_get_transactions_orders_latest_first():
    create_transaction_test_data()

    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Morning")
    insert_transaction(1, 200, 2, "2026-07-15 10:00:00", "Lunch")
    insert_transaction(1, 500, 1, "2026-07-15 09:00:00", "Bonus")

    transactions = get_transactions()

    assert all(
        isinstance(transaction, TransactionListRecord)
        for transaction in transactions
    )

    assert [
        transaction.transaction_id
        for transaction in transactions
    ] == [2, 3, 1]


def test_get_transactions_can_filter_by_account():
    create_transaction_test_data()

    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Cash income")
    insert_transaction(2, 500, 1, "2026-07-15 09:00:00", "Savings income")

    transactions = get_transactions(account_id=2)

    assert len(transactions) == 1
    assert transactions[0].account_name == "Savings"
    assert transactions[0].amount_centavos == 500


def test_get_transactions_can_filter_by_transaction_type():
    create_transaction_test_data()

    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Income")
    insert_transaction(1, 200, 2, "2026-07-15 09:00:00", "Expense")

    income_transactions = get_transactions(transaction_type="income")
    expense_transactions = get_transactions(transaction_type="expense")

    assert len(income_transactions) == 1
    assert income_transactions[0].transaction_type == "income"

    assert len(expense_transactions) == 1
    assert expense_transactions[0].transaction_type == "expense"


def test_get_transactions_can_search_notes_case_insensitively():
    create_transaction_test_data()

    insert_transaction(
        1,
        1000,
        1,
        "2026-07-15 08:00:00",
        "Monthly PAY",
    )
    insert_transaction(
        1,
        200,
        2,
        "2026-07-15 09:00:00",
        "Lunch",
    )

    transactions = get_transactions(search_text="monthly")

    assert [
        transaction.transaction_id
        for transaction in transactions
    ] == [1]


def test_get_transactions_can_search_account_names():
    create_transaction_test_data()

    insert_transaction(
        1,
        1000,
        1,
        "2026-07-15 08:00:00",
        "Income",
    )
    insert_transaction(
        2,
        500,
        1,
        "2026-07-15 09:00:00",
        "Income",
    )

    transactions = get_transactions(search_text="sav")

    assert [
        transaction.transaction_id
        for transaction in transactions
    ] == [2]


def test_get_transactions_can_search_category_group_names():
    create_transaction_test_data()

    insert_transaction(
        1,
        1000,
        1,
        "2026-07-15 08:00:00",
        None,
    )
    insert_transaction(
        1,
        200,
        2,
        "2026-07-15 09:00:00",
        None,
    )

    transactions = get_transactions(search_text="foo")

    assert [
        transaction.transaction_id
        for transaction in transactions
    ] == [2]


def test_get_transactions_can_search_category_names():
    create_transaction_test_data()

    insert_transaction(
        1,
        1000,
        1,
        "2026-07-15 08:00:00",
        None,
    )
    insert_transaction(
        1,
        200,
        2,
        "2026-07-15 09:00:00",
        None,
    )

    transactions = get_transactions(search_text="check")

    assert [
        transaction.transaction_id
        for transaction in transactions
    ] == [1]


def test_get_transactions_search_treats_sql_wildcards_as_text():
    create_transaction_test_data()

    insert_transaction(
        1,
        1000,
        1,
        "2026-07-15 08:00:00",
        "100% saved",
    )
    insert_transaction(
        1,
        500,
        1,
        "2026-07-15 09:00:00",
        "1000 saved",
    )
    insert_transaction(
        1,
        250,
        1,
        "2026-07-15 10:00:00",
        r"Budget\_plan",
    )

    percent_matches = get_transactions(search_text="100%")
    escaped_matches = get_transactions(search_text=r"\_")

    assert [
        transaction.transaction_id
        for transaction in percent_matches
    ] == [1]
    assert [
        transaction.transaction_id
        for transaction in escaped_matches
    ] == [3]


def test_get_transactions_search_returns_empty_list_when_unmatched():
    create_transaction_test_data()
    insert_transaction(
        1,
        1000,
        1,
        "2026-07-15 08:00:00",
        "Income",
    )

    assert get_transactions(search_text="missing") == []


def test_get_transactions_can_limit_results():
    create_transaction_test_data()

    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "First")
    insert_transaction(1, 500, 1, "2026-07-15 09:00:00", "Second")
    insert_transaction(1, 200, 2, "2026-07-15 10:00:00", "Third")

    transactions = get_transactions(limit=2)

    assert len(transactions) == 2
    assert [
        transaction.transaction_id
        for transaction in transactions
    ] == [3, 2]


def test_get_transactions_can_filter_by_category_group():
    create_transaction_test_data()

    insert_transaction(
        1,
        1000,
        1,
        "2026-07-15 08:00:00",
        "Income",
    )
    insert_transaction(
        1,
        200,
        2,
        "2026-07-15 09:00:00",
        "Lunch",
    )

    transactions = get_transactions(group_id=2)

    assert [
        transaction.transaction_id
        for transaction in transactions
    ] == [2]


def test_get_transactions_can_filter_by_category():
    create_transaction_test_data()
    insert_category(2, "Dinner")

    insert_transaction(
        1,
        200,
        2,
        "2026-07-15 08:00:00",
        "Lunch",
    )
    insert_transaction(
        1,
        300,
        3,
        "2026-07-15 09:00:00",
        "Dinner",
    )

    transactions = get_transactions(category_id=2)

    assert [
        transaction.transaction_id
        for transaction in transactions
    ] == [1]


def test_get_transactions_includes_entire_selected_date_range():
    create_transaction_test_data()

    insert_transaction(
        1,
        100,
        1,
        "2026-07-14 23:59:59",
        "Before",
    )
    insert_transaction(
        1,
        200,
        1,
        "2026-07-15 00:00:00",
        "Start",
    )
    insert_transaction(
        1,
        300,
        1,
        "2026-07-15 23:59:59",
        "End",
    )
    insert_transaction(
        1,
        400,
        1,
        "2026-07-16 00:00:00",
        "After",
    )

    transactions = get_transactions(
        start_date=date(2026, 7, 15),
        end_date=date(2026, 7, 15),
    )

    assert [
        transaction.transaction_id
        for transaction in transactions
    ] == [3, 2]


def test_get_transactions_supports_open_ended_date_ranges():
    create_transaction_test_data()

    insert_transaction(
        1,
        100,
        1,
        "2026-07-14 12:00:00",
        "First",
    )
    insert_transaction(
        1,
        200,
        1,
        "2026-07-15 12:00:00",
        "Second",
    )
    insert_transaction(
        1,
        300,
        1,
        "2026-07-16 12:00:00",
        "Third",
    )

    transactions_from_date = get_transactions(
        start_date=date(2026, 7, 15),
    )
    transactions_through_date = get_transactions(
        end_date=date(2026, 7, 15),
    )

    assert [
        transaction.transaction_id
        for transaction in transactions_from_date
    ] == [3, 2]
    assert [
        transaction.transaction_id
        for transaction in transactions_through_date
    ] == [2, 1]


def test_get_transactions_combines_all_repository_filters():
    create_transaction_test_data()

    insert_transaction(
        1,
        200,
        2,
        "2026-07-15 08:00:00",
        "Team lunch",
    )
    insert_transaction(
        2,
        200,
        2,
        "2026-07-15 09:00:00",
        "Team lunch",
    )
    insert_transaction(
        1,
        1000,
        1,
        "2026-07-15 10:00:00",
        "Team income",
    )
    insert_transaction(
        1,
        200,
        2,
        "2026-07-16 08:00:00",
        "Team lunch",
    )
    insert_transaction(
        1,
        200,
        2,
        "2026-07-15 11:00:00",
        "Dinner",
    )

    transactions = get_transactions(
        search_text="team",
        account_id=1,
        transaction_type="expense",
        group_id=2,
        category_id=2,
        start_date=date(2026, 7, 15),
        end_date=date(2026, 7, 15),
    )

    assert [
        transaction.transaction_id
        for transaction in transactions
    ] == [1]


def test_get_transactions_applies_filters_before_limit():
    create_transaction_test_data()

    insert_transaction(
        1,
        1000,
        1,
        "2026-07-15 08:00:00",
        "Matching income",
    )
    insert_transaction(
        1,
        200,
        2,
        "2026-07-15 10:00:00",
        "Newer expense",
    )

    transactions = get_transactions(
        transaction_type="income",
        limit=1,
    )

    assert [
        transaction.transaction_id
        for transaction in transactions
    ] == [1]


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
    assert transaction == TransactionDetailRecord(
        transaction_id=1,
        account_id=2,
        amount_centavos=750,
        category_id=2,
        date_time="2026-07-15 12:30:00",
        notes="Updated",
        account_name="Savings",
        category_name="Lunch",
        group_id=2,
        group_name="Food",
        transaction_type="expense",
    )


def test_update_missing_transaction_returns_false():
    create_transaction_test_data()

    result = update_transaction(
        account_id=1,
        amount_centavos=750,
        category_id=1,
        date_time="2026-07-15 12:30:00",
        notes="Missing",
        transaction_id=999,
    )

    assert result is False


def test_delete_transaction():
    create_transaction_test_data()
    insert_transaction(1, 1000, 1, "2026-07-15 08:00:00", "Income")

    result = delete_transaction(1)

    assert result is True
    assert get_transactions() == []


def test_delete_missing_transaction_returns_false():
    result = delete_transaction(999)

    assert result is False


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


def test_restore_transaction_preserves_original_record():
    create_transaction_test_data()
    insert_transaction(
        1,
        1000,
        1,
        "2026-07-15 08:00:00",
        "Income",
    )
    transaction = get_transaction_by_id(1)

    assert delete_transaction(1) is True
    assert restore_transaction(transaction) is True
    assert get_transaction_by_id(1) == transaction
