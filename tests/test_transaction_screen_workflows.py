from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock
from datetime import date

import pytest

from database.records import (
    AccountRecord,
    CategoryGroupRecord,
    CategoryRecord,
    TransactionDetailRecord,
)

from screens.add_transaction import AddTransactionScreen
from screens.transaction_form_state import TransactionFormState
from screens.transaction_filter_state import TransactionFilterState
from screens.transactions import TransactionsScreen

from services.transaction_services import (
    TransactionPostResult,
    TransactionSaveResult,
)


action_results_module = import_module("screens.action_results")


def test_transaction_search_normalizes_and_debounces(
    monkeypatch,
):
    transactions_module = import_module("screens.transactions")
    pending_event = SimpleNamespace(cancel=Mock())
    scheduled_event = object()
    clock = SimpleNamespace(
        schedule_once=Mock(return_value=scheduled_event)
    )
    monkeypatch.setattr(
        transactions_module,
        "Clock",
        clock,
    )
    screen = SimpleNamespace(
        filter_state=TransactionFilterState(),
        _search_refresh_event=pending_event,
        _suspend_search_refresh=False,
        apply_search_text=Mock(),
    )
    screen.cancel_pending_search_refresh = lambda: (
        TransactionsScreen.cancel_pending_search_refresh(
            screen
        )
    )

    TransactionsScreen.set_search_text(
        screen,
        "  team lunch  ",
    )

    assert screen.filter_state.search_text == "team lunch"
    pending_event.cancel.assert_called_once_with()
    clock.schedule_once.assert_called_once_with(
        screen.apply_search_text,
        transactions_module.SEARCH_REFRESH_DELAY,
    )
    assert screen._search_refresh_event is scheduled_event


def test_clear_transaction_search_preserves_type_filter():
    search_field = SimpleNamespace(text="team lunch")
    screen = SimpleNamespace(
        filter_state=TransactionFilterState(
            search_text="team lunch",
            transaction_type="expense",
        ),
        _search_refresh_event=None,
        _suspend_search_refresh=False,
        ids=SimpleNamespace(
            transaction_search=search_field,
        ),
        load_transactions=Mock(),
        render_advanced_filter_state=Mock(),
    )
    screen.cancel_pending_search_refresh = lambda: (
        TransactionsScreen.cancel_pending_search_refresh(
            screen
        )
    )
    screen.set_search_field_text = lambda search_text: (
        TransactionsScreen.set_search_field_text(
            screen,
            search_text,
        )
    )

    TransactionsScreen.clear_search(screen)

    assert screen.filter_state.search_text == ""
    assert screen.filter_state.transaction_type == "expense"
    assert search_field.text == ""
    screen.load_transactions.assert_called_once_with()
    screen.render_advanced_filter_state.assert_called_once_with()


def test_show_all_transactions_resets_search_and_type_filters():
    search_field = SimpleNamespace(text="team lunch")
    all_filter = SimpleNamespace(set_selected=Mock())
    income_filter = SimpleNamespace(set_selected=Mock())
    expense_filter = SimpleNamespace(set_selected=Mock())
    screen = SimpleNamespace(
        filter_state=TransactionFilterState(
            search_text="team lunch",
            transaction_type="expense",
        ),
        _search_refresh_event=None,
        _suspend_search_refresh=False,
        ids=SimpleNamespace(
            transaction_search=search_field,
            all_filter=all_filter,
            income_filter=income_filter,
            expense_filter=expense_filter,
        ),
        load_transactions=Mock(),
        render_advanced_filter_state=Mock(),
    )
    screen.cancel_pending_search_refresh = lambda: (
        TransactionsScreen.cancel_pending_search_refresh(
            screen
        )
    )
    screen.render_filter_state = lambda: (
        TransactionsScreen.render_filter_state(screen)
    )
    screen.set_search_field_text = lambda search_text: (
        TransactionsScreen.set_search_field_text(
            screen,
            search_text,
        )
    )

    TransactionsScreen.show_all_transactions(screen)

    assert screen.filter_state == TransactionFilterState()
    assert search_field.text == ""
    all_filter.set_selected.assert_called_once_with(True)
    income_filter.set_selected.assert_called_once_with(False)
    expense_filter.set_selected.assert_called_once_with(False)
    screen.load_transactions.assert_called_once_with()
    screen.render_advanced_filter_state.assert_called_once_with()


def test_transaction_history_resets_filters_on_pre_enter():
    screen = SimpleNamespace(
        filter_state=TransactionFilterState(
            search_text="lunch",
            transaction_type="expense",
            group_id=3,
            group_name="Food",
            category_id=5,
            category_name="Dining",
        ),
        cancel_pending_search_refresh=Mock(),
        render_filter_state=Mock(),
        set_search_field_text=Mock(),
        load_transactions=Mock(),
        render_advanced_filter_state=Mock(),
    )

    TransactionsScreen.on_pre_enter(screen)

    assert screen.filter_state == TransactionFilterState()
    screen.cancel_pending_search_refresh.assert_called_once_with()
    screen.render_filter_state.assert_called_once_with()
    screen.set_search_field_text.assert_called_once_with("")
    screen.load_transactions.assert_called_once_with()
    screen.render_advanced_filter_state.assert_called_once_with()


def test_transaction_history_renders_transfer_type_filter():
    all_filter = SimpleNamespace(set_selected=Mock())
    income_filter = SimpleNamespace(set_selected=Mock())
    expense_filter = SimpleNamespace(set_selected=Mock())
    transfer_filter = SimpleNamespace(set_selected=Mock())
    screen = SimpleNamespace(
        filter_state=TransactionFilterState(
            transaction_type="transfer",
        ),
        ids=SimpleNamespace(
            all_filter=all_filter,
            income_filter=income_filter,
            expense_filter=expense_filter,
            transfer_filter=transfer_filter,
        ),
    )

    TransactionsScreen.render_filter_state(screen)

    all_filter.set_selected.assert_called_once_with(False)
    income_filter.set_selected.assert_called_once_with(False)
    expense_filter.set_selected.assert_called_once_with(False)
    transfer_filter.set_selected.assert_called_once_with(True)


def test_transfer_type_disables_category_only_filters():
    group_filter = SimpleNamespace(disabled=False, opacity=1)
    category_filter = SimpleNamespace(disabled=False, opacity=1)
    screen = SimpleNamespace(
        filter_state=TransactionFilterState(
            transaction_type="transfer",
        ),
        ids=SimpleNamespace(
            account_filter_label=SimpleNamespace(text=""),
            group_filter_label=SimpleNamespace(text=""),
            category_filter_label=SimpleNamespace(text=""),
            group_filter=group_filter,
            category_filter=category_filter,
            start_date_filter_label=SimpleNamespace(text=""),
            end_date_filter_label=SimpleNamespace(text=""),
            active_filters_label=SimpleNamespace(text=""),
            reset_all_filters=SimpleNamespace(
                disabled=True,
                opacity=.38,
            ),
        ),
    )

    TransactionsScreen.render_advanced_filter_state(screen)

    assert group_filter.disabled is True
    assert group_filter.opacity == .38
    assert category_filter.disabled is True
    assert category_filter.opacity == .38
    assert screen.ids.active_filters_label.text == "Active: Transfer"


def test_transaction_history_load_forwards_filter_state(
    monkeypatch,
):
    transactions_module = import_module("screens.transactions")
    filter_state = TransactionFilterState(
        search_text="lunch",
        transaction_type="expense",
    )
    list_data = {
        "activities": [],
        "empty_state": {
            "title": "No matching transactions",
            "message": (
                "Try changing or resetting your search and filters."
            ),
        },
    }
    get_activity_list_data = Mock(return_value=list_data)
    render_transaction_history = Mock()
    action_callback = Mock()
    screen = SimpleNamespace(
        filter_state=filter_state,
        ids=SimpleNamespace(
            transactions_recycle_view=object(),
            transaction_empty_state_container=object(),
        ),
        get_empty_transaction_action=Mock(
            return_value=("SHOW ALL", action_callback)
        ),
    )
    monkeypatch.setattr(
        transactions_module,
        "get_activity_list_data",
        get_activity_list_data,
    )
    monkeypatch.setattr(
        transactions_module,
        "render_transaction_history",
        render_transaction_history,
    )

    TransactionsScreen.load_transactions(screen)

    get_activity_list_data.assert_called_once_with(
        **filter_state.to_query_arguments()
    )
    render_transaction_history.assert_called_once_with(
        recycle_view=screen.ids.transactions_recycle_view,
        empty_state_container=(
            screen.ids.transaction_empty_state_container
        ),
        transactions=[],
        screen=screen,
        empty_state=list_data["empty_state"],
        action_text="SHOW ALL",
        action_callback=action_callback,
    )


def make_save_screen(
    *,
    transaction_id=None,
    posting_status="posted",
):
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
            posting_status=posting_status,
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


def patch_post_workflow(monkeypatch, result):
    add_transaction_module = import_module(
        "screens.add_transaction"
    )
    post_transaction_workflow = Mock(return_value=result)
    show_snackbar = Mock()

    monkeypatch.setattr(
        add_transaction_module,
        "post_transaction_workflow",
        post_transaction_workflow,
    )
    monkeypatch.setattr(
        action_results_module,
        "show_snackbar",
        show_snackbar,
    )

    return post_transaction_workflow, show_snackbar


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
        posting_status="posted",
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
        posting_status="posted",
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
        posting_status="posted",
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
        posting_status="posted",
    )

    assert screen.form_state.transaction_id == 17

    show_snackbar.assert_called_once_with(
        "Transaction could not be updated."
    )
    dashboard.load_dashboard.assert_not_called()
    screen.manager.get_screen.assert_not_called()

    assert screen.manager.current == "add_transaction"


def test_save_as_temporary_uses_explicit_temporary_status(
    monkeypatch,
):
    save_transaction_workflow, show_snackbar = (
        patch_save_workflow(
            monkeypatch,
            TransactionSaveResult(
                success=True,
                message="Temporary transaction saved.",
            ),
        )
    )
    screen, dashboard = make_save_screen()

    AddTransactionScreen.save_temporary_transaction(screen)

    save_transaction_workflow.assert_called_once_with(
        account_id=2,
        amount="123.45",
        transaction_type="expense",
        category_id=8,
        date_label="July 19, 2026",
        time_label="7:30 PM",
        notes_label="Dinner",
        transaction_id=None,
        posting_status="temporary",
    )
    show_snackbar.assert_called_once_with(
        "Temporary transaction saved."
    )
    dashboard.load_dashboard.assert_called_once_with()
    assert screen.manager.current == "dashboard"


def test_save_temporary_edit_preserves_edit_state_on_failure(
    monkeypatch,
):
    save_transaction_workflow, show_snackbar = (
        patch_save_workflow(
            monkeypatch,
            TransactionSaveResult(
                success=False,
                message=(
                    "Temporary transaction could not be updated."
                ),
            ),
        )
    )
    screen, dashboard = make_save_screen(
        transaction_id=17,
        posting_status="temporary",
    )

    AddTransactionScreen.save_temporary_transaction(screen)

    save_transaction_workflow.assert_called_once_with(
        account_id=2,
        amount="123.45",
        transaction_type="expense",
        category_id=8,
        date_label="July 19, 2026",
        time_label="7:30 PM",
        notes_label="Dinner",
        transaction_id=17,
        posting_status="temporary",
    )
    show_snackbar.assert_called_once_with(
        "Temporary transaction could not be updated."
    )
    dashboard.load_dashboard.assert_not_called()
    assert screen.form_state.transaction_id == 17
    assert screen.manager.current == "add_transaction"


def test_post_temporary_edit_saves_current_values_before_posting(
    monkeypatch,
):
    save_transaction_workflow, _ = patch_save_workflow(
        monkeypatch,
        TransactionSaveResult(
            success=True,
            message="Temporary transaction updated successfully.",
        ),
    )
    post_transaction_workflow, show_snackbar = (
        patch_post_workflow(
            monkeypatch,
            TransactionPostResult(
                success=True,
                message="Temporary transaction posted.",
            ),
        )
    )
    screen, dashboard = make_save_screen(
        transaction_id=17,
        posting_status="temporary",
    )

    AddTransactionScreen.post_transaction(screen)

    save_transaction_workflow.assert_called_once_with(
        account_id=2,
        amount="123.45",
        transaction_type="expense",
        category_id=8,
        date_label="July 19, 2026",
        time_label="7:30 PM",
        notes_label="Dinner",
        transaction_id=17,
        posting_status="temporary",
    )
    post_transaction_workflow.assert_called_once_with(17)
    show_snackbar.assert_called_once_with(
        "Temporary transaction posted."
    )
    dashboard.load_dashboard.assert_called_once_with()
    assert screen.form_state.transaction_id is None
    assert screen.form_state.posting_status == "posted"
    assert screen.manager.current == "dashboard"


def test_post_temporary_edit_stops_when_current_values_do_not_save(
    monkeypatch,
):
    save_transaction_workflow, _ = (
        patch_save_workflow(
            monkeypatch,
            TransactionSaveResult(
                success=False,
                message="Please select an account.",
            ),
        )
    )
    post_transaction_workflow, show_snackbar = patch_post_workflow(
        monkeypatch,
        TransactionPostResult(
            success=True,
            message="Temporary transaction posted.",
        ),
    )
    screen, dashboard = make_save_screen(
        transaction_id=17,
        posting_status="temporary",
    )

    AddTransactionScreen.post_transaction(screen)

    save_transaction_workflow.assert_called_once()
    post_transaction_workflow.assert_not_called()
    show_snackbar.assert_called_once_with(
        "Please select an account."
    )
    dashboard.load_dashboard.assert_not_called()
    assert screen.form_state.transaction_id == 17
    assert screen.manager.current == "add_transaction"


def test_post_temporary_edit_keeps_temporary_state_when_post_fails(
    monkeypatch,
):
    save_transaction_workflow, _ = patch_save_workflow(
        monkeypatch,
        TransactionSaveResult(
            success=True,
            message="Temporary transaction updated successfully.",
        ),
    )
    post_transaction_workflow, show_snackbar = (
        patch_post_workflow(
            monkeypatch,
            TransactionPostResult(
                success=False,
                message="Temporary transaction could not be posted.",
            ),
        )
    )
    screen, dashboard = make_save_screen(
        transaction_id=17,
        posting_status="temporary",
    )

    AddTransactionScreen.post_transaction(screen)

    save_transaction_workflow.assert_called_once()
    post_transaction_workflow.assert_called_once_with(17)
    show_snackbar.assert_called_once_with(
        "Temporary transaction could not be posted."
    )
    dashboard.load_dashboard.assert_not_called()
    assert screen.form_state.transaction_id == 17
    assert screen.form_state.posting_status == "temporary"
    assert screen.manager.current == "add_transaction"


def test_posted_edit_cannot_be_saved_as_temporary(
    monkeypatch,
):
    save_transaction_workflow, show_snackbar = (
        patch_save_workflow(
            monkeypatch,
            TransactionSaveResult(
                success=True,
                message="Unexpected save.",
            ),
        )
    )
    screen, dashboard = make_save_screen(
        transaction_id=17,
        posting_status="posted",
    )

    AddTransactionScreen.save_temporary_transaction(screen)

    save_transaction_workflow.assert_not_called()
    show_snackbar.assert_called_once_with(
        "Posted transactions cannot be changed back to temporary."
    )
    dashboard.load_dashboard.assert_not_called()
    assert screen.form_state.transaction_id == 17
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
        select_created_account=Mock(),
    )

    AddTransactionScreen.open_add_account_screen(screen)

    assert manager.current == "accounts"
    assert screen.form_state is form_state
    account_menu.dismiss.assert_called_once_with()
    manager.get_screen.assert_called_once_with("accounts")
    assert accounts_screen.return_screen == "add_transaction"
    assert screen.preserve_form_on_next_enter is True
    assert (
        accounts_screen.account_created_callback
        is screen.select_created_account
    )


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
        select_created_group=Mock(),
        select_created_category=Mock(),
    )

    AddTransactionScreen.open_manage_category_screen(screen)

    assert manager.current == "categories"
    assert screen.form_state is form_state
    groups_menu.dismiss.assert_called_once_with()
    categories_menu.dismiss.assert_called_once_with()
    manager.get_screen.assert_called_once_with("categories")
    assert categories_screen.return_screen == "add_transaction"
    assert screen.preserve_form_on_next_enter is True
    assert (
        categories_screen.group_created_callback
        is screen.select_created_group
    )
    assert (
        categories_screen.category_created_callback
        is screen.select_created_category
    )
    assert categories_screen.initial_transaction_type == "income"
    assert categories_screen.initial_group_id is None


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
        reconcile_preserved_selections=Mock(),
        render_form_state=Mock(),
    )

    AddTransactionScreen.on_pre_enter(screen)

    screen.reset_form.assert_not_called()
    screen.reconcile_preserved_selections.assert_called_once_with()
    screen.render_form_state.assert_called_once_with()
    assert screen.preserve_form_on_next_enter is False

    AddTransactionScreen.on_pre_enter(screen)

    screen.reset_form.assert_called_once_with()


def test_reconcile_preserved_selections_clears_deleted_values(monkeypatch):
    add_transaction_module = import_module("screens.add_transaction")
    get_all_accounts = Mock(
        return_value=[AccountRecord(account_id=9, name="Savings")]
    )
    get_groups = Mock(
        return_value=[
            CategoryGroupRecord(
                group_id=5,
                name="Food",
                transaction_type="expense",
            )
        ]
    )
    get_categories = Mock(
        return_value=[
            CategoryRecord(
                category_id=12,
                group_id=5,
                name="Groceries",
                group_name="Food",
                transaction_type="expense",
            )
        ]
    )
    monkeypatch.setattr(
        add_transaction_module,
        "get_all_accounts",
        get_all_accounts,
    )
    monkeypatch.setattr(
        add_transaction_module,
        "get_category_groups_by_type",
        get_groups,
    )
    monkeypatch.setattr(
        add_transaction_module,
        "get_categories_by_group",
        get_categories,
    )
    screen = SimpleNamespace(
        form_state=TransactionFormState(
            transaction_type="expense",
            account_id=2,
            account_name="Cash",
            group_id=5,
            group_name="Food",
            category_id=8,
            category_name="Dining",
        )
    )

    AddTransactionScreen.reconcile_preserved_selections(screen)

    assert screen.form_state.account_id is None
    assert screen.form_state.account_name == "Select Account"
    assert screen.form_state.group_id == 5
    assert screen.form_state.group_name == "Food"
    assert screen.form_state.category_id is None
    assert screen.form_state.category_name == "Select Category"
    get_all_accounts.assert_called_once_with()
    get_groups.assert_called_once_with("expense")
    get_categories.assert_called_once_with(5)


def test_reconcile_preserved_selections_clears_deleted_group(monkeypatch):
    add_transaction_module = import_module("screens.add_transaction")
    get_groups = Mock(return_value=[])
    get_categories = Mock()
    monkeypatch.setattr(
        add_transaction_module,
        "get_category_groups_by_type",
        get_groups,
    )
    monkeypatch.setattr(
        add_transaction_module,
        "get_categories_by_group",
        get_categories,
    )
    screen = SimpleNamespace(
        form_state=TransactionFormState(
            transaction_type="expense",
            group_id=5,
            group_name="Food",
            category_id=8,
            category_name="Dining",
        )
    )

    AddTransactionScreen.reconcile_preserved_selections(screen)

    assert screen.form_state.group_id is None
    assert screen.form_state.group_name == "Select Category Group"
    assert screen.form_state.category_id is None
    assert (
        screen.form_state.category_name
        == "No Category Group Selected"
    )
    get_groups.assert_called_once_with("expense")
    get_categories.assert_not_called()


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
        "EnkryonSelectionPanel",
        menu_factory,
    )

    screen = SimpleNamespace(
        form_state=TransactionFormState(),
        ids=SimpleNamespace(
            account_selector=account_selector,
            account_label=SimpleNamespace(text=""),
        ),
        open_add_account_screen=open_add_account_screen,
    )

    AddTransactionScreen.open_account_menu(screen)

    get_all_accounts.assert_called_once_with()
    assert screen.ids.account_label.text == "No Accounts"
    assert screen.account_menu is menu
    menu.open.assert_called_once_with()

    panel_kwargs = menu_factory.call_args.kwargs

    assert panel_kwargs["title"] == "Select Account"
    assert panel_kwargs["selected_text"] == screen.form_state.account_name

    menu_items = panel_kwargs["options"]

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
        "EnkryonSelectionPanel",
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

    menu_items = menu_factory.call_args.kwargs["options"]
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
        "EnkryonSelectionPanel",
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

    menu_items = menu_factory.call_args.kwargs["options"]
    assert [item["text"] for item in menu_items] == [
        "Manage Categories"
    ]

    menu_items[0]["on_release"]()

    open_manage_category_screen.assert_called_once_with()


def test_created_account_is_selected_in_preserved_form(monkeypatch):
    add_transaction_module = import_module(
        "screens.add_transaction"
    )
    monkeypatch.setattr(
        add_transaction_module,
        "get_all_accounts",
        Mock(
            return_value=[
                AccountRecord(account_id=9, name="Savings")
            ]
        ),
    )
    screen = SimpleNamespace(
        form_state=TransactionFormState(account_name="No Accounts"),
        render_form_state=Mock(),
    )

    AddTransactionScreen.select_created_account(screen, "Savings")

    assert screen.form_state.account_id == 9
    assert screen.form_state.account_name == "Savings"
    screen.render_form_state.assert_called_once_with()


def test_created_group_is_selected_in_preserved_form(monkeypatch):
    add_transaction_module = import_module(
        "screens.add_transaction"
    )
    get_groups = Mock(
        return_value=[
            CategoryGroupRecord(
                group_id=6,
                name="Food",
                transaction_type="expense",
            )
        ]
    )
    monkeypatch.setattr(
        add_transaction_module,
        "get_category_groups_by_type",
        get_groups,
    )
    screen = SimpleNamespace(
        form_state=TransactionFormState(
            transaction_type="expense",
            group_name="No Category Groups Created",
        ),
        render_form_state=Mock(),
    )

    AddTransactionScreen.select_created_group(
        screen,
        "expense",
        "Food",
    )

    get_groups.assert_called_once_with("expense")
    assert screen.form_state.transaction_type == "expense"
    assert screen.form_state.group_id == 6
    assert screen.form_state.group_name == "Food"
    assert screen.form_state.category_id is None
    assert screen.form_state.category_name == "Select Category"
    screen.render_form_state.assert_called_once_with()


def test_created_category_is_selected_in_preserved_form(monkeypatch):
    add_transaction_module = import_module(
        "screens.add_transaction"
    )
    get_categories = Mock(
        return_value=[
            CategoryRecord(
                category_id=12,
                group_id=6,
                name="Dining",
                group_name="Food",
                transaction_type="expense",
            )
        ]
    )
    monkeypatch.setattr(
        add_transaction_module,
        "get_categories_by_group",
        get_categories,
    )
    screen = SimpleNamespace(
        form_state=TransactionFormState(
            transaction_type="expense",
            category_name="No Category Created",
        ),
        render_form_state=Mock(),
    )

    AddTransactionScreen.select_created_category(
        screen,
        6,
        "Dining",
    )

    get_categories.assert_called_once_with(6)
    assert screen.form_state.transaction_type == "expense"
    assert screen.form_state.group_id == 6
    assert screen.form_state.group_name == "Food"
    assert screen.form_state.category_id == 12
    assert screen.form_state.category_name == "Dining"
    screen.render_form_state.assert_called_once_with()


def test_transaction_history_renders_advanced_filter_state():
    state = TransactionFilterState(
        search_text="lunch",
        transaction_type="expense",
        account_id=2,
        account_name="Cash",
        group_id=5,
        group_name="Food",
        category_id=8,
        category_name="Dining",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 20),
    )
    category_filter = SimpleNamespace(
        disabled=True,
        opacity=.38,
    )
    reset_all_filters = SimpleNamespace(
        disabled=True,
        opacity=.38,
    )
    screen = SimpleNamespace(
        filter_state=state,
        ids=SimpleNamespace(
            account_filter_label=SimpleNamespace(text=""),
            group_filter_label=SimpleNamespace(text=""),
            category_filter_label=SimpleNamespace(text=""),
            category_filter=category_filter,
            start_date_filter_label=SimpleNamespace(text=""),
            end_date_filter_label=SimpleNamespace(text=""),
            active_filters_label=SimpleNamespace(text=""),
            reset_all_filters=reset_all_filters,
        ),
    )

    TransactionsScreen.render_advanced_filter_state(screen)

    assert screen.ids.account_filter_label.text == "Cash"
    assert screen.ids.group_filter_label.text == "Food"
    assert screen.ids.category_filter_label.text == "Dining"
    assert category_filter.disabled is False
    assert category_filter.opacity == 1
    assert (
        screen.ids.start_date_filter_label.text
        == "From: 2026-07-01"
    )
    assert (
        screen.ids.end_date_filter_label.text
        == "Through: 2026-07-20"
    )
    assert screen.ids.active_filters_label.text == (
        "Active: "
        + " • ".join(state.active_filter_labels)
    )
    assert reset_all_filters.disabled is False
    assert reset_all_filters.opacity == 1


def test_transaction_history_account_filter_menu(
    monkeypatch,
):
    transactions_module = import_module("screens.transactions")
    accounts = [
        AccountRecord(2, "Cash"),
        AccountRecord(3, "Savings"),
    ]
    get_all_accounts = Mock(return_value=accounts)
    panel = SimpleNamespace(open=Mock())
    panel_factory = Mock(return_value=panel)
    screen = SimpleNamespace(
        filter_state=TransactionFilterState(
            account_id=2,
            account_name="Cash",
        ),
        select_account_filter=Mock(),
    )
    monkeypatch.setattr(
        transactions_module,
        "get_all_accounts",
        get_all_accounts,
    )
    monkeypatch.setattr(
        transactions_module,
        "EnkryonSelectionPanel",
        panel_factory,
    )

    TransactionsScreen.open_account_filter_menu(screen)

    get_all_accounts.assert_called_once_with()
    assert screen.account_filter_menu is panel
    panel.open.assert_called_once_with()

    options = panel_factory.call_args.kwargs["options"]
    assert [option["text"] for option in options] == [
        "All Accounts",
        "Cash",
        "Savings",
    ]
    assert options[1]["selected"] is True

    options[0]["on_release"]()
    screen.select_account_filter.assert_called_once_with(
        None,
        "All Accounts",
    )


def test_transaction_history_group_filter_uses_type(
    monkeypatch,
):
    transactions_module = import_module("screens.transactions")
    groups = [
        CategoryGroupRecord(5, "Food", "expense"),
    ]
    get_groups = Mock(return_value=groups)
    panel = SimpleNamespace(open=Mock())
    panel_factory = Mock(return_value=panel)
    screen = SimpleNamespace(
        filter_state=TransactionFilterState(
            transaction_type="expense",
        ),
        select_group_filter=Mock(),
    )
    monkeypatch.setattr(
        transactions_module,
        "get_category_groups_by_type",
        get_groups,
    )
    monkeypatch.setattr(
        transactions_module,
        "EnkryonSelectionPanel",
        panel_factory,
    )

    TransactionsScreen.open_group_filter_menu(screen)

    get_groups.assert_called_once_with("expense")
    options = panel_factory.call_args.kwargs["options"]
    assert [option["text"] for option in options] == [
        "All Category Groups",
        "Food",
    ]
    panel.open.assert_called_once_with()


def test_transaction_history_category_filter_uses_group(
    monkeypatch,
):
    transactions_module = import_module("screens.transactions")
    categories = [
        CategoryRecord(
            8,
            5,
            "Dining",
            "Food",
            "expense",
        ),
    ]
    get_categories = Mock(return_value=categories)
    panel = SimpleNamespace(open=Mock())
    panel_factory = Mock(return_value=panel)
    screen = SimpleNamespace(
        filter_state=TransactionFilterState(
            group_id=5,
            group_name="Food",
        ),
        select_category_filter=Mock(),
    )
    monkeypatch.setattr(
        transactions_module,
        "get_categories_by_group",
        get_categories,
    )
    monkeypatch.setattr(
        transactions_module,
        "EnkryonSelectionPanel",
        panel_factory,
    )

    TransactionsScreen.open_category_filter_menu(screen)

    get_categories.assert_called_once_with(5)
    options = panel_factory.call_args.kwargs["options"]
    assert [option["text"] for option in options] == [
        "All Categories",
        "Dining",
    ]
    panel.open.assert_called_once_with()


def test_transaction_history_group_selection_refreshes():
    state = TransactionFilterState(
        group_id=3,
        group_name="Transport",
        category_id=7,
        category_name="Fuel",
    )
    panel = SimpleNamespace(dismiss=Mock())
    screen = SimpleNamespace(
        filter_state=state,
        group_filter_menu=panel,
        refresh_transaction_list=Mock(),
    )

    TransactionsScreen.select_group_filter(
        screen,
        5,
        "Food",
    )

    assert state.group_id == 5
    assert state.group_name == "Food"
    assert state.category_id is None
    assert state.category_name == "All Categories"
    panel.dismiss.assert_called_once_with()
    screen.refresh_transaction_list.assert_called_once_with()


def test_transaction_history_date_filters_remain_valid():
    state = TransactionFilterState(
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 20),
    )
    screen = SimpleNamespace(
        filter_state=state,
        refresh_transaction_list=Mock(),
    )

    TransactionsScreen.set_start_date_filter(
        screen,
        date(2026, 7, 25),
    )

    assert state.start_date == date(2026, 7, 25)
    assert state.end_date is None

    state.set_date_range(
        date(2026, 7, 1),
        date(2026, 7, 20),
    )

    TransactionsScreen.set_end_date_filter(
        screen,
        date(2026, 6, 30),
    )

    assert state.start_date is None
    assert state.end_date == date(2026, 6, 30)
    assert screen.refresh_transaction_list.call_count == 2


def test_transaction_history_category_selection_refreshes():
    state = TransactionFilterState(
        transaction_type="expense",
        group_id=5,
        group_name="Food",
    )
    panel = SimpleNamespace(dismiss=Mock())
    screen = SimpleNamespace(
        filter_state=state,
        category_filter_menu=panel,
        refresh_transaction_list=Mock(),
    )

    TransactionsScreen.select_category_filter(
        screen,
        8,
        "Dining",
    )

    assert state.transaction_type == "expense"
    assert state.group_id == 5
    assert state.group_name == "Food"
    assert state.category_id == 8
    assert state.category_name == "Dining"
    panel.dismiss.assert_called_once_with()
    screen.refresh_transaction_list.assert_called_once_with()
