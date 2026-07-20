from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from services import category_services
from services.category_services import CategoryActionResult


def patch_repository_action(
    monkeypatch,
    action_name,
    repository_result,
):
    service_module = import_module("services.category_services")
    action = Mock(return_value=repository_result)
    monkeypatch.setattr(service_module, action_name, action)
    return action


def test_get_groups_for_view_forwards_transaction_type(monkeypatch):
    groups = [
        SimpleNamespace(
            group_id=1,
            name="Food",
            transaction_type="expense",
        )
    ]
    get_category_groups_by_type = Mock(return_value=groups)
    monkeypatch.setattr(
        category_services,
        "get_category_groups_by_type",
        get_category_groups_by_type,
    )

    result = category_services.get_groups_for_view("expense")

    get_category_groups_by_type.assert_called_once_with("expense")
    assert result is groups


@pytest.mark.parametrize(
    ("repository_result", "expected_result"),
    [
        (
            (True, None),
            CategoryActionResult(
                True,
                "Group 'Food' added successfully.",
                True,
            ),
        ),
        (
            (False, "empty"),
            CategoryActionResult(
                False,
                "Group name cannot be empty.",
            ),
        ),
        (
            (False, "duplicate"),
            CategoryActionResult(
                False,
                "Group name 'Food' already exists for this type.",
            ),
        ),
        (
            (False, "invalid_type"),
            CategoryActionResult(
                False,
                "Group could not be added.",
            ),
        ),
        (
            (False, "error"),
            CategoryActionResult(
                False,
                "Group could not be added.",
            ),
        ),
    ],
)
def test_create_group_returns_repository_outcome(
    monkeypatch,
    repository_result,
    expected_result,
):
    insert_category_group = patch_repository_action(
        monkeypatch,
        "insert_category_group",
        repository_result,
    )

    result = category_services.create_group(" Food ", "expense")

    insert_category_group.assert_called_once_with("Food", "expense")
    assert result == expected_result


@pytest.mark.parametrize(
    ("repository_result", "expected_result"),
    [
        (
            (True, None),
            CategoryActionResult(
                True,
                "Group renamed to 'Meals' successfully.",
                True,
            ),
        ),
        (
            (False, "empty"),
            CategoryActionResult(
                False,
                "New group name cannot be empty.",
            ),
        ),
        (
            (False, "duplicate"),
            CategoryActionResult(
                False,
                "Group name 'Meals' already exists for this type.",
            ),
        ),
        (
            (False, "not_found"),
            CategoryActionResult(
                False,
                "Group no longer exists.",
                True,
            ),
        ),
        (
            (False, "error"),
            CategoryActionResult(
                False,
                "Group could not be renamed.",
            ),
        ),
    ],
)
def test_rename_group_returns_repository_outcome(
    monkeypatch,
    repository_result,
    expected_result,
):
    update_category_group = patch_repository_action(
        monkeypatch,
        "update_category_group",
        repository_result,
    )

    result = category_services.rename_group(7, " Meals ")

    update_category_group.assert_called_once_with(7, "Meals")
    assert result == expected_result


@pytest.mark.parametrize(
    ("repository_result", "expected_result"),
    [
        (
            (True, None),
            CategoryActionResult(
                True,
                "Group deleted successfully.",
                True,
            ),
        ),
        (
            (False, "has_categories"),
            CategoryActionResult(
                False,
                "Cannot delete group because it still contains categories.",
            ),
        ),
        (
            (False, "error"),
            CategoryActionResult(
                False,
                "Group could not be deleted.",
            ),
        ),
    ],
)
def test_remove_group_returns_repository_outcome(
    monkeypatch,
    repository_result,
    expected_result,
):
    delete_category_group = patch_repository_action(
        monkeypatch,
        "delete_category_group",
        repository_result,
    )

    result = category_services.remove_group(7)

    delete_category_group.assert_called_once_with(7)
    assert result == expected_result


@pytest.mark.parametrize(
    ("repository_result", "expected_result"),
    [
        (
            (True, None),
            CategoryActionResult(
                True,
                "Category 'Dining' added successfully.",
                True,
            ),
        ),
        (
            (False, "empty"),
            CategoryActionResult(
                False,
                "Category name cannot be empty.",
            ),
        ),
        (
            (False, "duplicate"),
            CategoryActionResult(
                False,
                "Category name 'Dining' already exists for this type.",
            ),
        ),
        (
            (False, "group_not_found"),
            CategoryActionResult(
                False,
                "Category group no longer exists.",
                True,
            ),
        ),
        (
            (False, "error"),
            CategoryActionResult(
                False,
                "Category could not be added.",
            ),
        ),
    ],
)
def test_create_category_returns_repository_outcome(
    monkeypatch,
    repository_result,
    expected_result,
):
    insert_category = patch_repository_action(
        monkeypatch,
        "insert_category",
        repository_result,
    )

    result = category_services.create_category(7, " Dining ")

    insert_category.assert_called_once_with(7, "Dining")
    assert result == expected_result


@pytest.mark.parametrize(
    ("repository_result", "expected_result"),
    [
        (
            (True, None),
            CategoryActionResult(
                True,
                "Category renamed to 'Dinner' successfully.",
                True,
            ),
        ),
        (
            (False, "empty"),
            CategoryActionResult(
                False,
                "New category name cannot be empty.",
            ),
        ),
        (
            (False, "duplicate"),
            CategoryActionResult(
                False,
                "Category name 'Dinner' already exists for this type.",
            ),
        ),
        (
            (False, "not_found"),
            CategoryActionResult(
                False,
                "Category no longer exists.",
                True,
            ),
        ),
        (
            (False, "error"),
            CategoryActionResult(
                False,
                "Category could not be renamed.",
            ),
        ),
    ],
)
def test_rename_category_returns_repository_outcome(
    monkeypatch,
    repository_result,
    expected_result,
):
    update_category = patch_repository_action(
        monkeypatch,
        "update_category",
        repository_result,
    )

    result = category_services.rename_category(11, " Dinner ")

    update_category.assert_called_once_with(11, "Dinner")
    assert result == expected_result


@pytest.mark.parametrize(
    ("repository_result", "expected_result"),
    [
        (
            (True, None),
            CategoryActionResult(
                True,
                "Category deleted successfully.",
                True,
            ),
        ),
        (
            (False, "referenced"),
            CategoryActionResult(
                False,
                "Cannot delete category because it has existing transactions.",
            ),
        ),
        (
            (False, "error"),
            CategoryActionResult(
                False,
                "Category could not be deleted.",
            ),
        ),
    ],
)
def test_remove_category_returns_repository_outcome(
    monkeypatch,
    repository_result,
    expected_result,
):
    delete_category = patch_repository_action(
        monkeypatch,
        "delete_category",
        repository_result,
    )

    result = category_services.remove_category(11)

    delete_category.assert_called_once_with(11)
    assert result == expected_result
