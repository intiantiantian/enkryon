from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from screens.dashboard import DashboardScreen
from screens.transaction_filter_state import TransactionFilterState
from screens.transaction_list_actions import (
    TransactionListActionsMixin,
)
from screens.transactions import TransactionsScreen
from services.transaction_services import (
    TransactionDeleteResult,
    TransactionRestoreResult,
)

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
    state = TransactionFilterState(
        transaction_type="old-value",
    )
    screen = SimpleNamespace(
        filter_state=state,
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

    assert state.transaction_type == transaction_type
    all_filter.set_selected.assert_called_once_with(all_selected)
    income_filter.set_selected.assert_called_once_with(income_selected)
    expense_filter.set_selected.assert_called_once_with(expense_selected)
    screen.refresh_transaction_list.assert_called_once_with()


def test_set_transaction_filter_updates_shared_filter_state():
    state = TransactionFilterState(
        transaction_type="income",
        group_id=3,
        group_name="Salary",
        category_id=5,
        category_name="Paycheck",
    )
    screen = SimpleNamespace(
        filter_state=state,
        ids=SimpleNamespace(
            all_filter=SimpleNamespace(set_selected=Mock()),
            income_filter=SimpleNamespace(set_selected=Mock()),
            expense_filter=SimpleNamespace(set_selected=Mock()),
        ),
        refresh_transaction_list=Mock(),
    )

    TransactionListActionsMixin.set_transaction_filter(
        screen,
        "expense",
    )

    assert state.transaction_type == "expense"
    assert state.group_id is None
    assert state.category_id is None
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
        deleted_transaction=(object() if success else None),
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
    screen = SimpleNamespace(
        close_delete_transaction_dialog=Mock(),
        refresh_after_transaction_delete=Mock(),
        undo_transaction_delete=Mock(),
    )

    TransactionListActionsMixin.delete_transaction(screen, 17)

    delete_transaction_by_id.assert_called_once_with(17)
    screen.close_delete_transaction_dialog.assert_called_once_with()
    snackbar_call = show_snackbar.call_args
    assert snackbar_call.args == (service_result.message,)

    if success:
        assert snackbar_call.kwargs["action_text"] == "UNDO"
        assert snackbar_call.kwargs["duration"] == 8

        snackbar_call.kwargs["action_callback"]()

        screen.undo_transaction_delete.assert_called_once_with(
            service_result.deleted_transaction
        )
    else:
        assert snackbar_call.kwargs == {}
        screen.undo_transaction_delete.assert_not_called()


def test_confirm_delete_transaction_builds_working_dialog(
    monkeypatch,
):
    actions_module = import_module(
        "screens.transaction_list_actions"
    )
    dialog = SimpleNamespace(open=Mock())
    dialog_factory = Mock(return_value=dialog)
    monkeypatch.setattr(
        actions_module,
        "EnkryonConfirmationDialog",
        dialog_factory,
    )
    screen = SimpleNamespace(
        delete_transaction=Mock(),
        close_delete_transaction_dialog=Mock(),
    )

    TransactionListActionsMixin.confirm_delete_transaction(
        screen,
        17,
    )

    assert screen.delete_transaction_dialog is dialog
    dialog.open.assert_called_once_with()

    dialog_kwargs = dialog_factory.call_args.kwargs

    assert dialog_kwargs["title"] == "Delete Transaction?"
    assert (
        dialog_kwargs["message"]
        == "This transaction will be permanently deleted."
    )

    dialog_kwargs["confirm_callback"]()
    dialog_kwargs["cancel_callback"]()

    screen.delete_transaction.assert_called_once_with(17)
    screen.close_delete_transaction_dialog.assert_called_once_with()


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


def test_dashboard_reset_preserves_account_and_clears_type():
    state = TransactionFilterState(
        transaction_type="expense",
        account_id=7,
        account_name="Cash",
    )
    all_filter = SimpleNamespace(set_selected=Mock())
    income_filter = SimpleNamespace(set_selected=Mock())
    expense_filter = SimpleNamespace(set_selected=Mock())
    account_label = SimpleNamespace(text="")
    screen = SimpleNamespace(
        filter_state=state,
        ids=SimpleNamespace(
            all_filter=all_filter,
            income_filter=income_filter,
            expense_filter=expense_filter,
            account_label=account_label,
        ),
    )

    DashboardScreen.reset_dashboard(screen)

    assert state.transaction_type is None
    assert state.account_id == 7
    assert state.account_name == "Cash"
    all_filter.set_selected.assert_called_once_with(True)
    income_filter.set_selected.assert_called_once_with(False)
    expense_filter.set_selected.assert_called_once_with(False)
    assert account_label.text == "Cash"


def test_dashboard_recent_transactions_use_shared_filter_state(
    monkeypatch,
):
    dashboard_module = import_module("screens.dashboard")
    state = TransactionFilterState(
        transaction_type="expense",
        account_id=7,
        account_name="Cash",
    )
    get_transaction_list_data = Mock(
        return_value={
            "transactions": [],
            "empty_state": {},
        }
    )
    screen = SimpleNamespace(
        filter_state=state,
        ids=SimpleNamespace(
            transactions_container=object(),
        ),
        get_empty_transaction_action=Mock(
            return_value=("SHOW ALL", Mock())
        ),
    )

    monkeypatch.setattr(
        dashboard_module,
        "get_transaction_list_data",
        get_transaction_list_data,
    )
    monkeypatch.setattr(
        dashboard_module,
        "render_transaction_list",
        Mock(),
    )

    DashboardScreen.load_recent_transactions(screen)

    get_transaction_list_data.assert_called_once_with(
        **state.to_query_arguments(),
        limit=3,
        compact_empty_state=True,
    )


def test_transactions_screen_refreshes_full_transaction_list():
    screen = SimpleNamespace(
        cancel_pending_search_refresh=Mock(),
        load_transactions=Mock(),
        render_advanced_filter_state=Mock(),
    )

    TransactionsScreen.refresh_transaction_list(screen)

    screen.cancel_pending_search_refresh.assert_called_once_with()
    screen.load_transactions.assert_called_once_with()
    screen.render_advanced_filter_state.assert_called_once_with()


@pytest.mark.parametrize("success", [True, False])
def test_undo_transaction_delete_renders_restore_result(
    monkeypatch,
    success,
):
    actions_module = import_module(
        "screens.transaction_list_actions"
    )
    transaction = object()
    service_result = TransactionRestoreResult(
        success=success,
        message="Transaction restore result.",
    )
    restore_deleted_transaction = Mock(
        return_value=service_result
    )
    show_snackbar = Mock()
    monkeypatch.setattr(
        actions_module,
        "restore_deleted_transaction",
        restore_deleted_transaction,
    )
    monkeypatch.setattr(
        action_results_module,
        "show_snackbar",
        show_snackbar,
    )
    screen = SimpleNamespace(
        refresh_after_transaction_delete=Mock(),
    )

    TransactionListActionsMixin.undo_transaction_delete(
        screen,
        transaction,
    )

    restore_deleted_transaction.assert_called_once_with(
        transaction
    )
    show_snackbar.assert_called_once_with(service_result.message)
    assert (
        screen.refresh_after_transaction_delete.call_count
        == int(success)
    )


@pytest.mark.parametrize(
    (
        "transaction_filter",
        "selected_account_id",
        "expected_text",
        "callback_name",
    ),
    [
        (None, None, "ADD TRANSACTION", "go_to_add_transaction"),
        ("income", None, "SHOW ALL", "show_all_transactions"),
        (None, 7, "SHOW ALL", "show_all_transactions"),
    ],
)
def test_empty_transaction_action_matches_current_view(
    transaction_filter,
    selected_account_id,
    expected_text,
    callback_name,
):
    screen = SimpleNamespace(
        filter_state=TransactionFilterState(
            transaction_type=transaction_filter,
            account_id=selected_account_id,
            account_name=(
                "Cash"
                if selected_account_id is not None
                else "All Accounts"
            ),
        ),
        go_to_add_transaction=Mock(),
        show_all_transactions=Mock(),
    )

    action_text, action_callback = (
        TransactionListActionsMixin.get_empty_transaction_action(
            screen
        )
    )

    assert action_text == expected_text
    assert action_callback is getattr(screen, callback_name)


def test_empty_transaction_action_recognizes_search_state():
    screen = SimpleNamespace(
        filter_state=TransactionFilterState(
            search_text="lunch",
        ),
        go_to_add_transaction=Mock(),
        show_all_transactions=Mock(),
    )

    action_text, action_callback = (
        TransactionListActionsMixin
        .get_empty_transaction_action(screen)
    )

    assert action_text == "SHOW ALL"
    assert action_callback is screen.show_all_transactions


def test_show_all_transactions_clears_type_filter():
    screen = SimpleNamespace(set_transaction_filter=Mock())

    TransactionListActionsMixin.show_all_transactions(screen)

    screen.set_transaction_filter.assert_called_once_with(None)


def test_dashboard_show_all_clears_account_and_type_filters():
    state = TransactionFilterState(
        transaction_type="expense",
        account_id=7,
        account_name="Cash",
    )
    account_label = SimpleNamespace(text="Cash")
    screen = SimpleNamespace(
        filter_state=state,
        ids=SimpleNamespace(
            account_label=account_label,
        ),
        set_transaction_filter=Mock(),
        load_summary=Mock(),
    )

    DashboardScreen.show_all_transactions(screen)

    assert state == TransactionFilterState()
    assert account_label.text == "All Accounts"
    screen.set_transaction_filter.assert_called_once_with(None)
    screen.load_summary.assert_called_once_with()


def test_transactions_screen_can_open_add_transaction():
    manager = SimpleNamespace(current="transactions")
    screen = SimpleNamespace(manager=manager)

    TransactionsScreen.go_to_add_transaction(screen)

    assert manager.current == "add_transaction"
