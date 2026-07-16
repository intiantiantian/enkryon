from database.category_group_repository import (
    delete_category_group,
    get_category_groups_by_type,
    insert_category_group,
    update_category_group,
)


def test_insert_category_group():
    result, reason = insert_category_group("Food", "expense")

    assert result is True
    assert reason is None
    assert get_category_groups_by_type("expense") == [(1, "Food", "expense")]


def test_reject_empty_category_group_name():
    result, reason = insert_category_group("   ", "expense")

    assert result is False
    assert reason == "empty"
    assert get_category_groups_by_type("expense") == []


def test_reject_duplicate_category_group_name_for_same_type():
    insert_category_group("Food", "expense")

    result, reason = insert_category_group(" food ", "expense")

    assert result is False
    assert reason == "duplicate"
    assert get_category_groups_by_type("expense") == [(1, "Food", "expense")]


def test_allow_same_category_group_name_for_different_type():
    insert_category_group("Bonus", "income")

    result, reason = insert_category_group("Bonus", "expense")

    assert result is True
    assert reason is None
    assert get_category_groups_by_type("income") == [(1, "Bonus", "income")]
    assert get_category_groups_by_type("expense") == [(2, "Bonus", "expense")]


def test_update_category_group():
    insert_category_group("Food", "expense")

    result, reason = update_category_group(1, "Meals")

    assert result is True
    assert reason is None
    assert get_category_groups_by_type("expense") == [(1, "Meals", "expense")]


def test_delete_unused_category_group():
    insert_category_group("Food", "expense")

    result, reason = delete_category_group(1)

    assert result is True
    assert reason is None
    assert get_category_groups_by_type("expense") == []


def test_reject_invalid_category_group_type():
    result, reason = insert_category_group(
        "Transfer",
        "transfer",
    )

    assert result is False
    assert reason == "invalid_type"
    assert get_category_groups_by_type("transfer") == []