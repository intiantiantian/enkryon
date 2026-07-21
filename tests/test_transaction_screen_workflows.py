from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from database.records import TransactionDetailRecord

from screens.add_transaction import AddTransactionScreen
from screens.transaction_form_state import TransactionFormState

from services.transaction_services import TransactionSaveResult


action_results_module = import_module("screens.action_results")


def make_save_screen(*, transaction_id=None):
    dashboard = SimpleNamespace(load_dashboard=Mock())
    manager = SimpleNamespace(
        current="add_transaction",
        get_screen=Mock(return_value=dashboard),
    )
    screen = SimpleNamespace(
        form_state=TransactionFormState(
            amount="123.45",
            transaction_type="expense",
            account_id=2,
            account_name="Cash",
            group_id=5,
            group_name="Food",
            category_id=8,
            category_name="Dining",
            date_label="July 19, 2026",
            time_label="7:30 PM",
            notes="Dinner",
            transaction_id=transaction_id,
        ),
        manager=manager,
    )

    return screen, dashboard


def patch_save_workflow(monkeypatch, result):
    add_transaction_module = import_module(
        "screens.add_transaction"
    )
    save_transaction_workflow = Mock(
        return_value=result
    )
    show_snackbar = Mock()

    monkeypatch.setattr(
        add_transaction_module,
        "save_transaction_workflow",
        save_transaction_workflow,
    )
    monkeypatch.setattr(
        action_results_module,
        "show_snackbar",
        show_snackbar,
    )

    return save_transaction_workflow, show_snackbar


def test_save_transaction_stops_when_form_is_invalid(
    monkeypatch,
):
    save_transaction_workflow, show_snackbar = (
        patch_save_workflow(
            monkeypatch,
            TransactionSaveResult(
                success=False,
                message="Please select an account.",
            ),
        )
    )
    screen, dashboard = make_save_screen()

    AddTransactionScreen.save_transaction(screen)

    save_transaction_workflow.assert_called_once_with(
        account_id=2,
        amount="123.45",
        transaction_type="expense",
        category_id=8,
        date_label="July 19, 2026",
        time_label="7:30 PM",
        notes_label="Dinner",
        transaction_id=None,
    )
    show_snackbar.assert_called_once_with(
        "Please select an account."
    )
    dashboard.load_dashboard.assert_not_called()
    screen.manager.get_screen.assert_not_called()

    assert screen.manager.current == "add_transaction"


def test_save_transaction_creates_transaction_and_refreshes_dashboard(
    monkeypatch,
):
    save_transaction_workflow, show_snackbar = (
        patch_save_workflow(
            monkeypatch,
            TransactionSaveResult(
                success=True,
                message="Transaction added successfully.",
            ),
        )
    )
    screen, dashboard = make_save_screen()

    AddTransactionScreen.save_transaction(screen)

    save_transaction_workflow.assert_called_once_with(
        account_id=2,
        amount="123.45",
        transaction_type="expense",
        category_id=8,
        date_label="July 19, 2026",
        time_label="7:30 PM",
        notes_label="Dinner",
        transaction_id=None,
    )
    show_snackbar.assert_called_once_with(
        "Transaction added successfully."
    )

    assert screen.form_state.transaction_id is None

    screen.manager.get_screen.assert_called_once_with(
        "dashboard"
    )
    dashboard.load_dashboard.assert_called_once_with()

    assert screen.manager.current == "dashboard"


def test_save_transaction_updates_transaction_and_clears_edit_state(
    monkeypatch,
):
    save_transaction_workflow, show_snackbar = (
        patch_save_workflow(
            monkeypatch,
            TransactionSaveResult(
                success=True,
                message=(
                    "Transaction updated successfully."
                ),
            ),
        )
    )
    screen, dashboard = make_save_screen(
        transaction_id=17
    )

    AddTransactionScreen.save_transaction(screen)

    save_transaction_workflow.assert_called_once_with(
        account_id=2,
        amount="123.45",
        transaction_type="expense",
        category_id=8,
        date_label="July 19, 2026",
        time_label="7:30 PM",
        notes_label="Dinner",
        transaction_id=17,
    )

    assert screen.form_state.transaction_id is None

    show_snackbar.assert_called_once_with(
        "Transaction updated successfully."
    )
    dashboard.load_dashboard.assert_called_once_with()

    assert screen.manager.current == "dashboard"


def test_save_transaction_keeps_edit_state_when_update_fails(
    monkeypatch,
):
    save_transaction_workflow, show_snackbar = (
        patch_save_workflow(
            monkeypatch,
            TransactionSaveResult(
                success=False,
                message=(
                    "Transaction could not be updated."
                ),
            ),
        )
    )
    screen, dashboard = make_save_screen(
        transaction_id=17
    )

    AddTransactionScreen.save_transaction(screen)

    save_transaction_workflow.assert_called_once_with(
        account_id=2,
        amount="123.45",
        transaction_type="expense",
        category_id=8,
        date_label="July 19, 2026",
        time_label="7:30 PM",
        notes_label="Dinner",
        transaction_id=17,
    )

    assert screen.form_state.transaction_id == 17

    show_snackbar.assert_called_once_with(
        "Transaction could not be updated."
    )
    dashboard.load_dashboard.assert_not_called()
    screen.manager.get_screen.assert_not_called()

    assert screen.manager.current == "add_transaction"


def test_load_transaction_populates_edit_form(monkeypatch):
    add_transaction_module = import_module("screens.add_transaction")
    transaction = TransactionDetailRecord(
        transaction_id=17,
        account_id=2,
        amount_centavos=12345,
        category_id=8,
        date_time="2026-07-19 19:30:00",
        notes="Dinner",
        account_name="Cash",
        category_name="Dining",
        group_id=5,
        group_name="Food",
        transaction_type="expense",
    )
    get_transaction_for_edit = Mock(return_value=transaction)
    monkeypatch.setattr(
        add_transaction_module,
        "get_transaction_for_edit",
        get_transaction_for_edit,
    )
    screen = SimpleNamespace(
        render_form_state=Mock(),
    )

    AddTransactionScreen.load_transaction(screen, 17)

    get_transaction_for_edit.assert_called_once_with(17)
    assert screen.form_state == TransactionFormState(
        amount="123.45",
        transaction_type="expense",
        account_id=2,
        account_name="Cash",
        group_id=5,
        group_name="Food",
        category_id=8,
        category_name="Dining",
        date_label="2026-07-19",
        time_label="07:30 PM",
        notes="Dinner",
        transaction_id=17,
    )
    screen.render_form_state.assert_called_once_with()

def test_open_add_account_screen_preserves_in_progress_form():
    form_state = TransactionFormState(
        amount="800",
        transaction_type="income",
    )
    account_menu = SimpleNamespace(dismiss=Mock())
    screen = SimpleNamespace(
        form_state=form_state,
        manager=SimpleNamespace(current="add_transaction"),
        account_menu=account_menu,
    )

    AddTransactionScreen.open_add_account_screen(screen)

    assert screen.manager.current == "accounts"
    assert screen.form_state is form_state
    account_menu.dismiss.assert_called_once_with()


def test_open_manage_category_screen_preserves_in_progress_form():
    form_state = TransactionFormState(
        amount="800",
        transaction_type="income",
    )
    groups_menu = SimpleNamespace(dismiss=Mock())
    categories_menu = SimpleNamespace(dismiss=Mock())
    screen = SimpleNamespace(
        form_state=form_state,
        manager=SimpleNamespace(current="add_transaction"),
        groups_menu=groups_menu,
        categories_menu=categories_menu,
    )

    AddTransactionScreen.open_manage_category_screen(screen)

    assert screen.manager.current == "categories"
    assert screen.form_state is form_state
    groups_menu.dismiss.assert_called_once_with()
    categories_menu.dismiss.assert_called_once_with()


def test_add_transaction_pre_enter_resets_non_edit_form():
    screen = SimpleNamespace(
        form_state=TransactionFormState(transaction_id=None),
        reset_form=Mock(),
    )

    AddTransactionScreen.on_pre_enter(screen)

    screen.reset_form.assert_called_once_with()


def test_add_transaction_pre_enter_preserves_edit_form():
    screen = SimpleNamespace(
        form_state=TransactionFormState(transaction_id=17),
        reset_form=Mock(),
    )

    AddTransactionScreen.on_pre_enter(screen)

    screen.reset_form.assert_not_called()
