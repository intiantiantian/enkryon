from database.category_group_repository import insert_category_group
from database.category_repository import (
    delete_category,
    get_categories_by_group,
    get_categories_by_type,
    insert_category,
    update_category,
)
from database.records import CategoryRecord


def test_insert_category():
    insert_category_group("Food", "expense")

    result, reason = insert_category(1, "Lunch")

    assert result is True
    assert reason is None
    assert get_categories_by_group(1) == [
        CategoryRecord(
            category_id=1,
            group_id=1,
            name="Lunch",
            group_name="Food",
            transaction_type="expense",
        )
    ]


def test_reject_empty_category_name():
    insert_category_group("Food", "expense")

    result, reason = insert_category(1, "   ")

    assert result is False
    assert reason == "empty"
    assert get_categories_by_group(1) == []


def test_reject_category_when_group_does_not_exist():
    result, reason = insert_category(999, "Lunch")

    assert result is False
    assert reason == "group_not_found"


def test_reject_duplicate_category_name_for_same_transaction_type():
    insert_category_group("Food", "expense")
    insert_category_group("Bills", "expense")
    insert_category(1, "Lunch")

    result, reason = insert_category(2, " lunch ")

    assert result is False
    assert reason == "duplicate"


def test_allow_same_category_name_for_different_transaction_type():
    insert_category_group("Food", "expense")
    insert_category_group("Salary", "income")
    insert_category(1, "Bonus")

    result, reason = insert_category(2, "Bonus")

    assert result is True
    assert reason is None
    assert get_categories_by_type("expense") == [
        CategoryRecord(
            category_id=1,
            group_id=1,
            name="Bonus",
            group_name="Food",
            transaction_type="expense",
        )
    ]
    assert get_categories_by_type("income") == [
        CategoryRecord(
            category_id=2,
            group_id=2,
            name="Bonus",
            group_name="Salary",
            transaction_type="income",
        )
    ]


def test_update_category():
    insert_category_group("Food", "expense")
    insert_category(1, "Lunch")

    result, reason = update_category(1, "Dinner")

    assert result is True
    assert reason is None
    assert get_categories_by_group(1) == [
        CategoryRecord(
            category_id=1,
            group_id=1,
            name="Dinner",
            group_name="Food",
            transaction_type="expense",
        )
    ]


def test_delete_unused_category():
    insert_category_group("Food", "expense")
    insert_category(1, "Lunch")

    result, reason = delete_category(1)

    assert result is True
    assert reason is None
    assert get_categories_by_group(1) == []
