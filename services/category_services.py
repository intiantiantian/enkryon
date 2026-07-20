from typing import NamedTuple

from database.category_group_repository import (
    delete_category_group,
    get_category_groups_by_type,
    insert_category_group,
    update_category_group,
)
from database.category_repository import (
    delete_category,
    insert_category,
    update_category,
)


class CategoryActionResult(NamedTuple):
    success: bool
    message: str
    refresh_required: bool = False


def get_groups_for_view(transaction_type):
    return get_category_groups_by_type(transaction_type)


def create_group(group_name, transaction_type):
    group_name = (group_name or "").strip()
    success, reason = insert_category_group(
        group_name,
        transaction_type,
    )

    if success:
        return CategoryActionResult(
            True,
            f"Group '{group_name}' added successfully.",
            True,
        )

    messages = {
        "empty": "Group name cannot be empty.",
        "duplicate": (
            f"Group name '{group_name}' already exists for this type."
        ),
    }
    return CategoryActionResult(
        False,
        messages.get(reason, "Group could not be added."),
    )


def rename_group(group_id, new_name):
    new_name = (new_name or "").strip()
    success, reason = update_category_group(group_id, new_name)

    if success:
        return CategoryActionResult(
            True,
            f"Group renamed to '{new_name}' successfully.",
            True,
        )

    messages = {
        "empty": "New group name cannot be empty.",
        "duplicate": (
            f"Group name '{new_name}' already exists for this type."
        ),
        "not_found": "Group no longer exists.",
    }
    return CategoryActionResult(
        False,
        messages.get(reason, "Group could not be renamed."),
        refresh_required=reason == "not_found",
    )


def remove_group(group_id):
    success, reason = delete_category_group(group_id)

    if success:
        return CategoryActionResult(
            True,
            "Group deleted successfully.",
            True,
        )

    message = (
        "Cannot delete group because it still contains categories."
        if reason == "has_categories"
        else "Group could not be deleted."
    )
    return CategoryActionResult(False, message)


def create_category(group_id, category_name):
    category_name = (category_name or "").strip()
    success, reason = insert_category(group_id, category_name)

    if success:
        return CategoryActionResult(
            True,
            f"Category '{category_name}' added successfully.",
            True,
        )

    messages = {
        "empty": "Category name cannot be empty.",
        "duplicate": (
            f"Category name '{category_name}' already exists for this type."
        ),
        "group_not_found": "Category group no longer exists.",
    }
    return CategoryActionResult(
        False,
        messages.get(reason, "Category could not be added."),
        refresh_required=reason == "group_not_found",
    )


def rename_category(category_id, new_name):
    new_name = (new_name or "").strip()
    success, reason = update_category(category_id, new_name)

    if success:
        return CategoryActionResult(
            True,
            f"Category renamed to '{new_name}' successfully.",
            True,
        )

    messages = {
        "empty": "New category name cannot be empty.",
        "duplicate": (
            f"Category name '{new_name}' already exists for this type."
        ),
        "not_found": "Category no longer exists.",
    }
    return CategoryActionResult(
        False,
        messages.get(reason, "Category could not be renamed."),
        refresh_required=reason == "not_found",
    )


def remove_category(category_id):
    success, reason = delete_category(category_id)

    if success:
        return CategoryActionResult(
            True,
            "Category deleted successfully.",
            True,
        )

    message = (
        "Cannot delete category because it has existing transactions."
        if reason == "referenced"
        else "Category could not be deleted."
    )
    return CategoryActionResult(False, message)
