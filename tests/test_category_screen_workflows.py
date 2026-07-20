from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from screens.categories import CategoriesScreen
from services.category_services import CategoryActionResult


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
        categories_module,
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
    )

    CategoriesScreen.load_groups(screen)

    get_groups_for_view.assert_called_once_with(transaction_type)
    container.clear_widgets.assert_called_once_with()
    empty_state_factory.assert_called_once_with(
        icon="folder-outline",
        title=f"No {label} category groups yet",
        message="Tap + to create your first category group.",
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

    CategoriesScreen.save_group(screen, " Food ")

    create_group_workflow.assert_called_once_with(" Food ", "expense")
    show_snackbar.assert_called_once_with(result.message)
    assert screen.load_groups.call_count == expected_refresh_count


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
    screen = SimpleNamespace(load_groups=Mock())

    CategoriesScreen.save_category(screen, 7, " Dining ")

    create_category_workflow.assert_called_once_with(7, " Dining ")
    show_snackbar.assert_called_once_with(result.message)
    assert screen.load_groups.call_count == expected_refresh_count


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
