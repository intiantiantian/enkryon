from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from screens.categories import CategoriesScreen
from services.category_services import CategoryActionResult


action_results_module = import_module("screens.action_results")

ACTION_RESULTS = [
    pytest.param(
        CategoryActionResult(True, "Action succeeded.", True),
        1,
        id="success-refreshes",
    ),
    pytest.param(
        CategoryActionResult(False, "Action failed.", False),
        0,
        id="failure-does-not-refresh",
    ),
    pytest.param(
        CategoryActionResult(False, "Record is stale.", True),
        1,
        id="stale-failure-refreshes",
    ),
]


def patch_category_action(
    monkeypatch,
    action_name,
    result,
):
    categories_module = import_module("screens.categories")
    action = Mock(return_value=result)
    show_snackbar = Mock()
    monkeypatch.setattr(categories_module, action_name, action)
    monkeypatch.setattr(
        action_results_module,
        "show_snackbar",
        show_snackbar,
    )
    return action, show_snackbar


@pytest.mark.parametrize(
    ("transaction_type", "label"),
    [
        ("income", "income"),
        ("expense", "expense"),
    ],
)
def test_load_groups_renders_empty_state(
    monkeypatch,
    transaction_type,
    label,
):
    categories_module = import_module("screens.categories")
    get_groups_for_view = Mock(return_value=[])
    empty_state = object()
    empty_state_factory = Mock(return_value=empty_state)
    monkeypatch.setattr(
        categories_module,
        "get_groups_for_view",
        get_groups_for_view,
    )
    monkeypatch.setattr(
        categories_module,
        "EmptyState",
        empty_state_factory,
    )
    container = SimpleNamespace(
        clear_widgets=Mock(),
        add_widget=Mock(),
    )
    screen = SimpleNamespace(
        current_transaction_type=transaction_type,
        ids=SimpleNamespace(groups_container=container),
        add_group=Mock()
    )

    CategoriesScreen.load_groups(screen)

    get_groups_for_view.assert_called_once_with(transaction_type)
    container.clear_widgets.assert_called_once_with()
    empty_state_factory.assert_called_once_with(
        icon="folder-outline",
        title=f"No {label} category groups yet",
        message=(
            f"Create a group to organize your {label} categories."
        ),
        action_text="ADD GROUP",
        action_callback=screen.add_group,
    )
    container.add_widget.assert_called_once_with(empty_state)


def test_load_groups_renders_cards_and_restores_expansion(monkeypatch):
    categories_module = import_module("screens.categories")
    groups = [
        SimpleNamespace(group_id=1, name="Bills"),
        SimpleNamespace(group_id=2, name="Food"),
    ]
    get_groups_for_view = Mock(return_value=groups)
    cards = [
        SimpleNamespace(
            screen=None,
            set_group=Mock(),
            toggle_group=Mock(),
        ),
        SimpleNamespace(
            screen=None,
            set_group=Mock(),
            toggle_group=Mock(),
        ),
    ]
    category_group_card_factory = Mock(side_effect=cards)
    monkeypatch.setattr(
        categories_module,
        "get_groups_for_view",
        get_groups_for_view,
    )
    monkeypatch.setattr(
        categories_module,
        "CategoryGroupCard",
        category_group_card_factory,
    )
    container = SimpleNamespace(
        clear_widgets=Mock(),
        add_widget=Mock(),
    )
    screen = SimpleNamespace(
        current_transaction_type="expense",
        expanded_groups={2},
        ids=SimpleNamespace(groups_container=container),
    )

    CategoriesScreen.load_groups(screen)

    get_groups_for_view.assert_called_once_with("expense")
    container.clear_widgets.assert_called_once_with()
    assert category_group_card_factory.call_count == 2
    for card, group in zip(cards, groups):
        assert card.screen is screen
        card.set_group.assert_called_once_with(group)
    assert container.add_widget.call_args_list == [
        call(cards[0]),
        call(cards[1]),
    ]
    cards[0].toggle_group.assert_not_called()
    cards[1].toggle_group.assert_called_once_with()


@pytest.mark.parametrize(
    ("result", "expected_refresh_count"),
    ACTION_RESULTS,
)
def test_save_group_renders_service_result(
    monkeypatch,
    result,
    expected_refresh_count,
):
    create_group_workflow, show_snackbar = patch_category_action(
        monkeypatch,
        "create_group_workflow",
        result,
    )
    screen = SimpleNamespace(
        current_transaction_type="expense",
        load_groups=Mock(),
    )
    group_created_callback = Mock()
    screen = SimpleNamespace(
        current_transaction_type="expense",
        load_groups=Mock(),
        group_created_callback=group_created_callback,
    )

    CategoriesScreen.save_group(screen, " Food ")

    create_group_workflow.assert_called_once_with(" Food ", "expense")
    show_snackbar.assert_called_once_with(result.message)
    assert screen.load_groups.call_count == expected_refresh_count
    assert group_created_callback.call_args_list == (
        [call("expense", "Food")] if result.success else []
    )


@pytest.mark.parametrize(
    ("result", "expected_refresh_count"),
    ACTION_RESULTS,
)
def test_rename_group_renders_service_result(
    monkeypatch,
    result,
    expected_refresh_count,
):
    rename_group_workflow, show_snackbar = patch_category_action(
        monkeypatch,
        "rename_group_workflow",
        result,
    )
    screen = SimpleNamespace(load_groups=Mock())

    CategoriesScreen.rename_group(screen, 7, " Meals ")

    rename_group_workflow.assert_called_once_with(7, " Meals ")
    show_snackbar.assert_called_once_with(result.message)
    assert screen.load_groups.call_count == expected_refresh_count


@pytest.mark.parametrize(
    ("result", "expected_refresh_count"),
    ACTION_RESULTS,
)
def test_delete_group_renders_service_result(
    monkeypatch,
    result,
    expected_refresh_count,
):
    remove_group_workflow, show_snackbar = patch_category_action(
        monkeypatch,
        "remove_group_workflow",
        result,
    )
    screen = SimpleNamespace(
        close_delete_dialog=Mock(),
        load_groups=Mock(),
    )

    CategoriesScreen.perform_delete_group(screen, 7)

    screen.close_delete_dialog.assert_called_once_with()
    remove_group_workflow.assert_called_once_with(7)
    show_snackbar.assert_called_once_with(result.message)
    assert screen.load_groups.call_count == expected_refresh_count


@pytest.mark.parametrize(
    ("result", "expected_refresh_count"),
    ACTION_RESULTS,
)
def test_save_category_renders_service_result(
    monkeypatch,
    result,
    expected_refresh_count,
):
    create_category_workflow, show_snackbar = patch_category_action(
        monkeypatch,
        "create_category_workflow",
        result,
    )
    category_created_callback = Mock()
    screen = SimpleNamespace(
        load_groups=Mock(),
        category_created_callback=category_created_callback,
    )

    CategoriesScreen.save_category(screen, 7, " Dining ")

    create_category_workflow.assert_called_once_with(7, " Dining ")
    show_snackbar.assert_called_once_with(result.message)
    assert screen.load_groups.call_count == expected_refresh_count
    assert category_created_callback.call_args_list == (
        [call(7, "Dining")] if result.success else []
    )


@pytest.mark.parametrize(
    ("result", "expected_refresh_count"),
    ACTION_RESULTS,
)
def test_rename_category_renders_service_result(
    monkeypatch,
    result,
    expected_refresh_count,
):
    rename_category_workflow, show_snackbar = patch_category_action(
        monkeypatch,
        "rename_category_workflow",
        result,
    )
    screen = SimpleNamespace(load_groups=Mock())

    CategoriesScreen.rename_category(screen, 11, " Dinner ")

    rename_category_workflow.assert_called_once_with(11, " Dinner ")
    show_snackbar.assert_called_once_with(result.message)
    assert screen.load_groups.call_count == expected_refresh_count


@pytest.mark.parametrize(
    ("result", "expected_refresh_count"),
    ACTION_RESULTS,
)
def test_delete_category_renders_service_result(
    monkeypatch,
    result,
    expected_refresh_count,
):
    remove_category_workflow, show_snackbar = patch_category_action(
        monkeypatch,
        "remove_category_workflow",
        result,
    )
    screen = SimpleNamespace(
        close_delete_category_dialog=Mock(),
        load_groups=Mock(),
    )

    CategoriesScreen.perform_delete_category(screen, 11)

    screen.close_delete_category_dialog.assert_called_once_with()
    remove_category_workflow.assert_called_once_with(11)
    show_snackbar.assert_called_once_with(result.message)
    assert screen.load_groups.call_count == expected_refresh_count


@pytest.mark.parametrize(
    "return_screen",
    ["dashboard", "add_transaction"],
)
def test_category_back_returns_to_origin_once(return_screen):
    manager = SimpleNamespace(current="categories")
    screen = SimpleNamespace(
        manager=manager,
        return_screen=return_screen,
    )

    CategoriesScreen.go_back(screen)

    assert manager.current == return_screen
    assert screen.return_screen == "dashboard"


def test_category_entry_restores_transaction_context():
    income_button = SimpleNamespace(set_selected=Mock())
    expense_button = SimpleNamespace(set_selected=Mock())
    screen = SimpleNamespace(
        initial_transaction_type="expense",
        initial_group_id=7,
        ids=SimpleNamespace(
            income_button=income_button,
            expense_button=expense_button,
        ),
        load_groups=Mock(),
    )

    CategoriesScreen.on_pre_enter(screen)

    assert screen.current_transaction_type == "expense"
    assert screen.expanded_groups == {7}
    assert screen.initial_transaction_type is None
    assert screen.initial_group_id is None
    income_button.set_selected.assert_called_once_with(False)
    expense_button.set_selected.assert_called_once_with(True)
    screen.load_groups.assert_called_once_with()


def test_add_category_opens_creation_dialog(monkeypatch):
    categories_module = import_module("screens.categories")
    dialog = SimpleNamespace(open=Mock())
    dialog_factory = Mock(return_value=dialog)
    monkeypatch.setattr(
        categories_module,
        "InputDialog",
        dialog_factory,
    )
    screen = SimpleNamespace(save_category=Mock())

    CategoriesScreen.add_category(screen, 7)

    dialog_factory.assert_called_once()
    dialog.open.assert_called_once_with()

    dialog_options = dialog_factory.call_args.kwargs
    assert dialog_options["title"] == "New Category"
    assert dialog_options["hint_text"] == "Category name..."

    dialog_options["callback"](" Dining ")

    screen.save_category.assert_called_once_with(7, " Dining ")


@pytest.mark.parametrize(
    (
        "method_name",
        "dialog_attribute",
        "title",
        "message",
        "cancel_method",
        "delete_method",
    ),
    [
        (
            "confirm_delete_group",
            "delete_dialog",
            "Delete category group?",
            (
                "Empty category groups are deleted permanently. "
                "Groups containing categories cannot be deleted."
            ),
            "close_delete_dialog",
            "perform_delete_group",
        ),
        (
            "confirm_delete_category",
            "delete_category_dialog",
            "Delete category?",
            (
                "Unused categories are deleted permanently. "
                "Categories with existing transactions cannot be deleted."
            ),
            "close_delete_category_dialog",
            "perform_delete_category",
        ),
    ],
)
def test_delete_prompts_use_standard_confirmation(
    monkeypatch,
    method_name,
    dialog_attribute,
    title,
    message,
    cancel_method,
    delete_method,
):
    categories_module = import_module("screens.categories")
    dialog = object()
    confirmation = Mock(return_value=dialog)
    monkeypatch.setattr(
        categories_module,
        "open_permanent_delete_confirmation",
        confirmation,
    )
    cancel_callback = Mock()
    delete_callback_target = Mock()
    screen = SimpleNamespace()
    setattr(screen, cancel_method, cancel_callback)
    setattr(screen, delete_method, delete_callback_target)

    getattr(CategoriesScreen, method_name)(screen, 17)

    assert getattr(screen, dialog_attribute) is dialog
    options = confirmation.call_args.kwargs
    assert options["title"] == title
    assert options["message"] == message
    assert options["cancel_callback"] is cancel_callback

    options["delete_callback"]()

    delete_callback_target.assert_called_once_with(17)
