from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from screens.dashboard import DashboardScreen
from screens.transaction_filter_state import TransactionFilterState
from screens.transaction_list_actions import (
    TransactionListActionsMixin,
)
from screens.transactions import TransactionsScreen
from services.transaction_services import (
    TransactionDeleteResult,
    TransactionPostResult,
    TransactionRestoreResult,
)
from services.transfer_services import (
    TransferDeleteResult,
    TransferRestoreResult,
)

action_results_module = import_module("screens.action_results")


@pytest.mark.parametrize(
    (
        "transaction_type",
        "all_selected",
        "income_selected",
        "expense_selected",
        "transfer_selected",
    ),
    [
        (None, True, False, False, False),
        ("income", False, True, False, False),
        ("expense", False, False, True, False),
        ("transfer", False, False, False, True),
    ],
)
def test_set_transaction_filter_updates_buttons_and_refreshes(
    transaction_type,
    all_selected,
    income_selected,
    expense_selected,
    transfer_selected,
):
    all_filter = SimpleNamespace(set_selected=Mock())
    income_filter = SimpleNamespace(set_selected=Mock())
    expense_filter = SimpleNamespace(set_selected=Mock())
    transfer_filter = SimpleNamespace(set_selected=Mock())
    state = TransactionFilterState(
        transaction_type="old-value",
    )
    screen = SimpleNamespace(
        filter_state=state,
        ids=SimpleNamespace(
            all_filter=all_filter,
            income_filter=income_filter,
            expense_filter=expense_filter,
            transfer_filter=transfer_filter,
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
    transfer_filter.set_selected.assert_called_once_with(transfer_selected)
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
            transfer_filter=SimpleNamespace(set_selected=Mock()),
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


def test_edit_transfer_loads_form_before_navigation():
    transfer_screen = SimpleNamespace(load_transfer=Mock())
    manager = SimpleNamespace(
        current="dashboard",
        get_screen=Mock(return_value=transfer_screen),
    )
    screen = SimpleNamespace(manager=manager)

    TransactionListActionsMixin.edit_transfer(screen, 17)

    manager.get_screen.assert_called_once_with("transfer")
    transfer_screen.load_transfer.assert_called_once_with(17)
    assert manager.current == "transfer"


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


def test_confirm_delete_temporary_transaction_explains_non_posting_state(
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
        "temporary",
    )

    dialog_kwargs = dialog_factory.call_args.kwargs
    assert dialog_kwargs["title"] == (
        "Delete Pending Transaction?"
    )
    assert "does not currently affect financial totals" in (
        dialog_kwargs["message"]
    )


def test_confirm_post_transaction_builds_financial_effect_dialog(
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
        post_transaction=Mock(),
        close_post_transaction_dialog=Mock(),
    )

    TransactionListActionsMixin.confirm_post_transaction(
        screen,
        17,
    )

    assert screen.post_transaction_dialog is dialog
    dialog.open.assert_called_once_with()
    dialog_kwargs = dialog_factory.call_args.kwargs
    assert dialog_kwargs["title"] == (
        "Post Pending Transaction?"
    )
    assert "financially effective immediately" in (
        dialog_kwargs["message"]
    )
    assert "account balance and totals will update" in (
        dialog_kwargs["message"]
    )

    dialog_kwargs["confirm_callback"]()
    dialog_kwargs["cancel_callback"]()

    screen.post_transaction.assert_called_once_with(17)
    screen.close_post_transaction_dialog.assert_called_once_with()


@pytest.mark.parametrize("success", [True, False])
def test_post_transaction_renders_service_result(
    monkeypatch,
    success,
):
    actions_module = import_module(
        "screens.transaction_list_actions"
    )
    service_result = TransactionPostResult(
        success=success,
        message="Posting result.",
    )
    post_transaction_by_id = Mock(return_value=service_result)
    show_snackbar = Mock()
    monkeypatch.setattr(
        actions_module,
        "post_transaction_by_id",
        post_transaction_by_id,
    )
    monkeypatch.setattr(
        action_results_module,
        "show_snackbar",
        show_snackbar,
    )
    screen = SimpleNamespace(
        close_post_transaction_dialog=Mock(),
        refresh_after_transaction_post=Mock(),
    )

    TransactionListActionsMixin.post_transaction(screen, 17)

    post_transaction_by_id.assert_called_once_with(17)
    screen.close_post_transaction_dialog.assert_called_once_with()
    show_snackbar.assert_called_once_with(service_result.message)
    assert (
        screen.refresh_after_transaction_post.call_count
        == int(success)
    )


def test_confirm_delete_transfer_builds_working_dialog(monkeypatch):
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
        delete_transfer=Mock(),
        close_delete_transaction_dialog=Mock(),
    )

    TransactionListActionsMixin.confirm_delete_transfer(screen, 17)

    dialog_kwargs = dialog_factory.call_args.kwargs
    assert dialog_kwargs["title"] == "Delete Transfer?"
    assert dialog_kwargs["message"] == (
        "This transfer will be permanently deleted."
    )
    dialog_kwargs["confirm_callback"]()
    dialog_kwargs["cancel_callback"]()
    screen.delete_transfer.assert_called_once_with(17)
    screen.close_delete_transaction_dialog.assert_called_once_with()


def test_default_transaction_refresh_hooks_use_transaction_list_refresh():
    screen = SimpleNamespace(refresh_transaction_list=Mock())

    TransactionListActionsMixin.refresh_after_transaction_delete(
        screen
    )
    TransactionListActionsMixin.refresh_after_transaction_post(
        screen
    )

    assert screen.refresh_transaction_list.call_count == 2


def test_dashboard_defines_list_delete_and_post_refresh_hooks():
    screen = SimpleNamespace(
        load_recent_transactions=Mock(),
        load_dashboard=Mock(),
    )

    DashboardScreen.refresh_transaction_list(screen)
    DashboardScreen.refresh_after_transaction_delete(screen)
    DashboardScreen.refresh_after_transaction_post(screen)

    screen.load_recent_transactions.assert_called_once_with()
    assert screen.load_dashboard.call_count == 2


def test_dashboard_reset_preserves_account_and_clears_type():
    state = TransactionFilterState(
        transaction_type="expense",
        account_id=7,
        account_name="Cash",
    )
    all_filter = SimpleNamespace(set_selected=Mock())
    income_filter = SimpleNamespace(set_selected=Mock())
    expense_filter = SimpleNamespace(set_selected=Mock())
    transfer_filter = SimpleNamespace(set_selected=Mock())
    account_label = SimpleNamespace(text="")
    screen = SimpleNamespace(
        filter_state=state,
        ids=SimpleNamespace(
            all_filter=all_filter,
            income_filter=income_filter,
            expense_filter=expense_filter,
            transfer_filter=transfer_filter,
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
    transfer_filter.set_selected.assert_called_once_with(False)
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
    get_activity_list_data = Mock(
        return_value={
            "activities": [],
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
        "get_activity_list_data",
        get_activity_list_data,
    )
    monkeypatch.setattr(
        dashboard_module,
        "render_activity_list",
        Mock(),
    )

    DashboardScreen.load_recent_transactions(screen)

    get_activity_list_data.assert_called_once_with(
        **state.to_query_arguments(),
        limit=3,
        compact_empty_state=True,
    )


def test_dashboard_summary_uses_transfer_aware_balance_repository(
    monkeypatch,
):
    dashboard_module = import_module("screens.dashboard")
    get_current_balance_centavos = Mock(return_value=69_975)
    get_total_centavos = Mock(
        side_effect=lambda activity_type, _account_id: {
            "income": 100_000,
            "expense": 5_000,
        }[activity_type]
    )
    monkeypatch.setattr(
        dashboard_module,
        "get_current_balance_centavos",
        get_current_balance_centavos,
    )
    monkeypatch.setattr(
        dashboard_module,
        "get_total_centavos",
        get_total_centavos,
    )
    screen = SimpleNamespace(
        filter_state=TransactionFilterState(
            account_id=1,
            account_name="Cash",
        ),
        balance_visible=True,
        ids=SimpleNamespace(
            balance_label=SimpleNamespace(text=""),
            income_label=SimpleNamespace(text=""),
            expense_label=SimpleNamespace(text=""),
            eye_button=SimpleNamespace(icon=""),
        ),
    )

    DashboardScreen.load_summary(screen)

    get_current_balance_centavos.assert_called_once_with(1)
    assert get_total_centavos.call_args_list == [
        call("income", 1),
        call("expense", 1),
    ]
    assert screen.ids.balance_label.text == "₱ 699.75"
    assert screen.ids.income_label.text == "₱ 1,000.00"
    assert screen.ids.expense_label.text == "₱ 50.00"
    assert screen.ids.eye_button.icon == "eye"


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


@pytest.mark.parametrize("success", [True, False])
def test_delete_transfer_renders_service_result(monkeypatch, success):
    actions_module = import_module(
        "screens.transaction_list_actions"
    )
    deleted_transfer = object() if success else None
    result = TransferDeleteResult(
        success=success,
        message="Transfer deletion result.",
        deleted_transfer=deleted_transfer,
    )
    delete_transfer_by_id = Mock(return_value=result)
    show_snackbar = Mock()
    monkeypatch.setattr(
        actions_module,
        "delete_transfer_by_id",
        delete_transfer_by_id,
    )
    monkeypatch.setattr(
        action_results_module,
        "show_snackbar",
        show_snackbar,
    )
    screen = SimpleNamespace(
        close_delete_transaction_dialog=Mock(),
        refresh_after_transaction_delete=Mock(),
        undo_transfer_delete=Mock(),
    )

    TransactionListActionsMixin.delete_transfer(screen, 17)

    delete_transfer_by_id.assert_called_once_with(17)
    snackbar_call = show_snackbar.call_args
    assert snackbar_call.args == (result.message,)
    if success:
        snackbar_call.kwargs["action_callback"]()
        screen.undo_transfer_delete.assert_called_once_with(
            deleted_transfer
        )
    else:
        assert snackbar_call.kwargs == {}


@pytest.mark.parametrize("success", [True, False])
def test_undo_transfer_delete_renders_restore_result(
    monkeypatch,
    success,
):
    actions_module = import_module(
        "screens.transaction_list_actions"
    )
    transfer = object()
    result = TransferRestoreResult(
        success=success,
        message="Transfer restore result.",
    )
    restore_deleted_transfer = Mock(return_value=result)
    show_snackbar = Mock()
    monkeypatch.setattr(
        actions_module,
        "restore_deleted_transfer",
        restore_deleted_transfer,
    )
    monkeypatch.setattr(
        action_results_module,
        "show_snackbar",
        show_snackbar,
    )
    screen = SimpleNamespace(
        refresh_after_transaction_delete=Mock(),
    )

    TransactionListActionsMixin.undo_transfer_delete(
        screen,
        transfer,
    )

    restore_deleted_transfer.assert_called_once_with(transfer)
    show_snackbar.assert_called_once_with(result.message)
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
