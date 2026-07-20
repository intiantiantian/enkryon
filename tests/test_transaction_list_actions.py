from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from screens.dashboard import DashboardScreen
from screens.transaction_list_actions import (
    TransactionListActionsMixin,
)
from screens.transactions import TransactionsScreen
from services.transaction_services import TransactionDeleteResult


action_results_module = import_module("screens.action_results")


@pytest.mark.parametrize(
    (
        "transaction_type",
        "all_selected",
        "income_selected",
        "expense_selected",
    ),
    [
        (None, True, False, False),
        ("income", False, True, False),
        ("expense", False, False, True),
    ],
)
def test_set_transaction_filter_updates_buttons_and_refreshes(
    transaction_type,
    all_selected,
    income_selected,
    expense_selected,
):
    all_filter = SimpleNamespace(set_selected=Mock())
    income_filter = SimpleNamespace(set_selected=Mock())
    expense_filter = SimpleNamespace(set_selected=Mock())
    screen = SimpleNamespace(
        transaction_filter="old-value",
        ids=SimpleNamespace(
            all_filter=all_filter,
            income_filter=income_filter,
            expense_filter=expense_filter,
        ),
        refresh_transaction_list=Mock(),
    )

    TransactionListActionsMixin.set_transaction_filter(
        screen,
        transaction_type,
    )

    assert screen.transaction_filter == transaction_type
    all_filter.set_selected.assert_called_once_with(all_selected)
    income_filter.set_selected.assert_called_once_with(income_selected)
    expense_filter.set_selected.assert_called_once_with(expense_selected)
    screen.refresh_transaction_list.assert_called_once_with()


def test_edit_transaction_loads_form_before_navigation():
    add_transaction_screen = SimpleNamespace(load_transaction=Mock())
    manager = SimpleNamespace(
        current="dashboard",
        get_screen=Mock(return_value=add_transaction_screen),
    )
    screen = SimpleNamespace(manager=manager)

    TransactionListActionsMixin.edit_transaction(screen, 17)

    manager.get_screen.assert_called_once_with("add_transaction")
    add_transaction_screen.load_transaction.assert_called_once_with(17)
    assert manager.current == "add_transaction"


@pytest.mark.parametrize("success", [True, False])
def test_delete_transaction_renders_service_result(
    monkeypatch,
    success,
):
    actions_module = import_module(
        "screens.transaction_list_actions"
    )
    service_result = TransactionDeleteResult(
        success=success,
        message="Transaction deletion result.",
    )
    delete_transaction_by_id = Mock(return_value=service_result)
    show_snackbar = Mock()
    monkeypatch.setattr(
        actions_module,
        "delete_transaction_by_id",
        delete_transaction_by_id,
    )
    monkeypatch.setattr(
        action_results_module,
        "show_snackbar",
        show_snackbar,
    )
    dismiss = Mock()
    screen = SimpleNamespace(
        delete_transaction_dialog=SimpleNamespace(dismiss=dismiss),
        refresh_after_transaction_delete=Mock(),
    )

    TransactionListActionsMixin.delete_transaction(screen, 17)

    delete_transaction_by_id.assert_called_once_with(17)
    dismiss.assert_called_once_with()
    show_snackbar.assert_called_once_with(service_result.message)
    assert (
        screen.refresh_after_transaction_delete.call_count
        == int(success)
    )


def test_confirm_delete_transaction_builds_working_dialog(monkeypatch):
    actions_module = import_module(
        "screens.transaction_list_actions"
    )
    cancel_button = object()
    delete_button = object()
    button_factory = Mock(
        side_effect=[cancel_button, delete_button]
    )
    dialog = SimpleNamespace(
        dismiss=Mock(),
        open=Mock(),
    )
    dialog_factory = Mock(return_value=dialog)
    monkeypatch.setattr(
        actions_module,
        "MDFlatButton",
        button_factory,
    )
    monkeypatch.setattr(
        actions_module,
        "MDDialog",
        dialog_factory,
    )
    screen = SimpleNamespace(delete_transaction=Mock())

    TransactionListActionsMixin.confirm_delete_transaction(screen, 17)

    assert screen.delete_transaction_dialog is dialog
    dialog_factory.assert_called_once_with(
        title="Confirm Delete",
        text="Are you sure you want to delete this transaction?",
        buttons=[cancel_button, delete_button],
    )
    dialog.open.assert_called_once_with()

    cancel_callback = button_factory.call_args_list[0].kwargs[
        "on_release"
    ]
    delete_callback = button_factory.call_args_list[1].kwargs[
        "on_release"
    ]

    cancel_callback(None)
    delete_callback(None)

    dialog.dismiss.assert_called_once_with()
    screen.delete_transaction.assert_called_once_with(17)


def test_default_delete_refresh_uses_transaction_list_refresh():
    screen = SimpleNamespace(refresh_transaction_list=Mock())

    TransactionListActionsMixin.refresh_after_transaction_delete(
        screen
    )

    screen.refresh_transaction_list.assert_called_once_with()


def test_dashboard_defines_list_and_delete_refresh_hooks():
    screen = SimpleNamespace(
        load_recent_transactions=Mock(),
        load_dashboard=Mock(),
    )

    DashboardScreen.refresh_transaction_list(screen)
    DashboardScreen.refresh_after_transaction_delete(screen)

    screen.load_recent_transactions.assert_called_once_with()
    screen.load_dashboard.assert_called_once_with()


def test_transactions_screen_refreshes_full_transaction_list():
    screen = SimpleNamespace(load_transactions=Mock())

    TransactionsScreen.refresh_transaction_list(screen)

    screen.load_transactions.assert_called_once_with()
