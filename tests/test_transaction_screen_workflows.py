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
    accounts_screen = SimpleNamespace(return_screen="dashboard")
    manager = SimpleNamespace(
        current="add_transaction",
        get_screen=Mock(return_value=accounts_screen),
    )
    screen = SimpleNamespace(
        form_state=form_state,
        manager=manager,
        account_menu=account_menu,
    )

    AddTransactionScreen.open_add_account_screen(screen)

    assert manager.current == "accounts"
    assert screen.form_state is form_state
    account_menu.dismiss.assert_called_once_with()
    manager.get_screen.assert_called_once_with("accounts")
    assert accounts_screen.return_screen == "add_transaction"
    assert screen.preserve_form_on_next_enter is True


def test_open_manage_category_screen_preserves_in_progress_form():
    form_state = TransactionFormState(
        amount="800",
        transaction_type="income",
    )
    groups_menu = SimpleNamespace(dismiss=Mock())
    categories_menu = SimpleNamespace(dismiss=Mock())
    categories_screen = SimpleNamespace(return_screen="dashboard")
    manager = SimpleNamespace(
        current="add_transaction",
        get_screen=Mock(return_value=categories_screen),
    )
    screen = SimpleNamespace(
        form_state=form_state,
        manager=manager,
        groups_menu=groups_menu,
        categories_menu=categories_menu,
    )

    AddTransactionScreen.open_manage_category_screen(screen)

    assert manager.current == "categories"
    assert screen.form_state is form_state
    groups_menu.dismiss.assert_called_once_with()
    categories_menu.dismiss.assert_called_once_with()
    manager.get_screen.assert_called_once_with("categories")
    assert categories_screen.return_screen == "add_transaction"
    assert screen.preserve_form_on_next_enter is True


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


def test_add_transaction_pre_enter_preserves_non_edit_form_once():
    screen = SimpleNamespace(
        form_state=TransactionFormState(transaction_id=None),
        preserve_form_on_next_enter=True,
        reset_form=Mock(),
    )

    AddTransactionScreen.on_pre_enter(screen)

    screen.reset_form.assert_not_called()
    assert screen.preserve_form_on_next_enter is False

    AddTransactionScreen.on_pre_enter(screen)

    screen.reset_form.assert_called_once_with()


def test_empty_account_menu_offers_add_account(monkeypatch):
    add_transaction_module = import_module(
        "screens.add_transaction"
    )
    get_all_accounts = Mock(return_value=[])
    menu = SimpleNamespace(open=Mock())
    menu_factory = Mock(return_value=menu)
    account_selector = SimpleNamespace(text="Select Account")
    open_add_account_screen = Mock()

    monkeypatch.setattr(
        add_transaction_module,
        "get_all_accounts",
        get_all_accounts,
    )
    monkeypatch.setattr(
        add_transaction_module,
        "MDDropdownMenu",
        menu_factory,
    )

    screen = SimpleNamespace(
        form_state=TransactionFormState(),
        ids=SimpleNamespace(
            account_selector=account_selector,
        ),
        open_add_account_screen=open_add_account_screen,
    )

    AddTransactionScreen.open_account_menu(screen)

    get_all_accounts.assert_called_once_with()
    assert account_selector.text == "No Accounts"
    assert screen.account_menu is menu
    menu.open.assert_called_once_with()

    menu_items = menu_factory.call_args.kwargs["items"]
    assert [item["text"] for item in menu_items] == [
        "Add New Account"
    ]

    menu_items[0]["on_release"]()

    open_add_account_screen.assert_called_once_with()


def test_empty_group_menu_offers_category_management(
    monkeypatch,
):
    add_transaction_module = import_module(
        "screens.add_transaction"
    )
    get_groups = Mock(return_value=[])
    menu = SimpleNamespace(open=Mock())
    menu_factory = Mock(return_value=menu)
    group_selector = object()
    group_label = SimpleNamespace(text="")
    open_manage_category_screen = Mock()

    monkeypatch.setattr(
        add_transaction_module,
        "get_category_groups_by_type",
        get_groups,
    )
    monkeypatch.setattr(
        add_transaction_module,
        "MDDropdownMenu",
        menu_factory,
    )

    screen = SimpleNamespace(
        form_state=TransactionFormState(
            transaction_type="expense",
        ),
        ids=SimpleNamespace(
            group_selector=group_selector,
            group_label=group_label,
        ),
        open_manage_category_screen=(
            open_manage_category_screen
        ),
    )

    AddTransactionScreen.open_groups_menu(screen)

    get_groups.assert_called_once_with("expense")
    assert group_label.text == "No Category Groups Created"
    assert screen.groups_menu is menu
    menu.open.assert_called_once_with()

    menu_items = menu_factory.call_args.kwargs["items"]
    assert [item["text"] for item in menu_items] == [
        "Manage Category Groups"
    ]

    menu_items[0]["on_release"]()

    open_manage_category_screen.assert_called_once_with()


def test_empty_category_menu_offers_category_management(
    monkeypatch,
):
    add_transaction_module = import_module(
        "screens.add_transaction"
    )
    get_categories = Mock(return_value=[])
    menu = SimpleNamespace(open=Mock())
    menu_factory = Mock(return_value=menu)
    category_selector = object()
    category_label = SimpleNamespace(text="")
    open_manage_category_screen = Mock()

    monkeypatch.setattr(
        add_transaction_module,
        "get_categories_by_group",
        get_categories,
    )
    monkeypatch.setattr(
        add_transaction_module,
        "MDDropdownMenu",
        menu_factory,
    )

    screen = SimpleNamespace(
        form_state=TransactionFormState(group_id=7),
        ids=SimpleNamespace(
            category_selector=category_selector,
            category_label=category_label,
        ),
        open_manage_category_screen=(
            open_manage_category_screen
        ),
    )

    AddTransactionScreen.open_categories_menu(screen)

    get_categories.assert_called_once_with(7)
    assert category_label.text == "No Category Created"
    assert screen.categories_menu is menu
    menu.open.assert_called_once_with()

    menu_items = menu_factory.call_args.kwargs["items"]
    assert [item["text"] for item in menu_items] == [
        "Manage Categories"
    ]

    menu_items[0]["on_release"]()

    open_manage_category_screen.assert_called_once_with()
