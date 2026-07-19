from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from database.records import TransactionDetailRecord

from screens.add_transaction import AddTransactionScreen
from screens.dashboard import DashboardScreen
from screens.transactions import TransactionsScreen

from services.transaction_services import TransactionSaveResult


def make_label(text=""):
    return SimpleNamespace(text=text)


def make_save_screen(*, editing_transaction_id=None):
    dashboard = SimpleNamespace(load_dashboard=Mock())
    manager = SimpleNamespace(
        current="add_transaction",
        get_screen=Mock(return_value=dashboard),
    )
    screen = SimpleNamespace(
        amount="123.45",
        ids=SimpleNamespace(
            date_label=make_label("July 19, 2026"),
            notes_label=make_label("Dinner"),
            time_label=make_label("7:30 PM"),
        ),
        manager=manager,
        selected_account_id=2,
        selected_category_id=8,
        transaction_type="expense",
    )

    if editing_transaction_id is not None:
        screen.editing_transaction_id = editing_transaction_id

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
        add_transaction_module,
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

    assert screen.editing_transaction_id is None

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
        editing_transaction_id=17
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

    assert screen.editing_transaction_id is None

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
        editing_transaction_id=17
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

    assert screen.editing_transaction_id == 17

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
    get_transaction_by_id = Mock(return_value=transaction)
    centavos_to_peso_text = Mock(return_value="123.45")
    split_database_datetime = Mock(
        return_value=("July 19, 2026", "7:30 PM")
    )

    monkeypatch.setattr(
        add_transaction_module,
        "get_transaction_by_id",
        get_transaction_by_id,
    )
    monkeypatch.setattr(
        add_transaction_module,
        "centavos_to_peso_text",
        centavos_to_peso_text,
    )
    monkeypatch.setattr(
        add_transaction_module,
        "split_database_datetime",
        split_database_datetime,
    )

    screen = SimpleNamespace(
        ids=SimpleNamespace(
            account_selector=make_label(),
            category_label=make_label(),
            category_selector=SimpleNamespace(disabled=True),
            date_label=make_label(),
            group_label=make_label(),
            time_label=make_label(),
        ),
        reset_form=Mock(),
        set_notes=Mock(),
        set_transaction_type=Mock(),
        update_amount_label=Mock(),
    )

    AddTransactionScreen.load_transaction(screen, 17)

    get_transaction_by_id.assert_called_once_with(17)
    screen.reset_form.assert_called_once_with()
    screen.set_transaction_type.assert_called_once_with("expense")

    assert screen.editing_transaction_id == 17
    assert screen.selected_account_id == 2
    assert screen.selected_group_id == 5
    assert screen.selected_category_id == 8
    assert screen.ids.account_selector.text == "Cash"
    assert screen.ids.group_label.text == "Food"
    assert screen.ids.category_label.text == "Dining"
    assert screen.ids.category_selector.disabled is False
    assert screen.amount == "123.45"

    centavos_to_peso_text.assert_called_once_with(12345)
    screen.update_amount_label.assert_called_once_with()
    screen.set_notes.assert_called_once_with("Dinner")
    split_database_datetime.assert_called_once_with(
        "2026-07-19 19:30:00"
    )

    assert screen.ids.date_label.text == "July 19, 2026"
    assert screen.ids.time_label.text == "7:30 PM"


@pytest.mark.parametrize(
    "screen_class",
    [DashboardScreen, TransactionsScreen],
)
def test_edit_transaction_loads_form_before_navigation(
    screen_class,
):
    add_transaction_screen = SimpleNamespace(
        load_transaction=Mock()
    )
    manager = SimpleNamespace(
        current="dashboard",
        get_screen=Mock(return_value=add_transaction_screen),
    )
    screen = SimpleNamespace(manager=manager)

    screen_class.edit_transaction(screen, 17)

    manager.get_screen.assert_called_once_with("add_transaction")
    add_transaction_screen.load_transaction.assert_called_once_with(
        17
    )

    assert manager.current == "add_transaction"


@pytest.mark.parametrize(
    ("screen_class", "refresh_method_name"),
    [
        (DashboardScreen, "load_dashboard"),
        (TransactionsScreen, "load_transactions"),
    ],
)
def test_delete_transaction_refreshes_current_view(
    monkeypatch,
    screen_class,
    refresh_method_name,
):
    screen_module = import_module(screen_class.__module__)
    delete_transaction_by_id = Mock(return_value=True)
    show_snackbar = Mock()

    monkeypatch.setattr(
        screen_module,
        "delete_transaction_by_id",
        delete_transaction_by_id,
    )
    monkeypatch.setattr(
        screen_module,
        "show_snackbar",
        show_snackbar,
    )

    dismiss = Mock()
    refresh = Mock()
    screen = SimpleNamespace(
        delete_transaction_dialog=SimpleNamespace(
            dismiss=dismiss
        ),
    )
    setattr(screen, refresh_method_name, refresh)

    screen_class.delete_transaction(screen, 17)

    delete_transaction_by_id.assert_called_once_with(17)
    dismiss.assert_called_once_with()
    refresh.assert_called_once_with()
    show_snackbar.assert_called_once_with(
        "Transaction deleted successfully."
    )
