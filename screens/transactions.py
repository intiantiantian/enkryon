from kivy.clock import Clock
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import Screen

from database.account_repository import get_all_accounts
from database.category_group_repository import (
    get_all_category_groups,
    get_category_groups_by_type,
)
from database.category_repository import get_categories_by_group

from .transaction_filter_state import TransactionFilterState
from .transaction_list_actions import TransactionListActionsMixin

from services.activity_services import (
    get_activity_list_data,
)

from widgets.transaction_list import render_transaction_history
from widgets.date_time_pickers import DatePickerDialog
from widgets.overlays import EnkryonSelectionPanel
from utils.transaction_posting import TEMPORARY_STATUS


SEARCH_REFRESH_DELAY = 0.25

class TransactionsScreen(TransactionListActionsMixin, Screen):
    advanced_filters_expanded = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.filter_state = TransactionFilterState()
        self._search_refresh_event = None
        self._suspend_search_refresh = False


    def go_to_dashboard(self):
        self.manager.current = 'dashboard'


    def go_to_add_transaction(self):
        self.manager.current = "add_transaction"


    def toggle_advanced_filters(self):
        self.advanced_filters_expanded = (
            not self.advanced_filters_expanded
        )


    def on_pre_enter(self):
        self.advanced_filters_expanded = False
        self.cancel_pending_search_refresh()
        self.filter_state.reset()
        self.render_filter_state()
        self.render_advanced_filter_state()
        self.set_search_field_text("")
        self.load_transactions()


    def render_filter_state(self):
        transaction_type = self.filter_state.transaction_type
        is_pending = (
            self.filter_state.posting_status == TEMPORARY_STATUS
        )

        self.ids.all_filter.set_selected(
            transaction_type is None and not is_pending
        )
        self.ids.income_filter.set_selected(
            transaction_type == "income" and not is_pending
        )
        self.ids.expense_filter.set_selected(
            transaction_type == "expense" and not is_pending
        )
        transfer_filter = getattr(
            self.ids,
            "transfer_filter",
            None,
        )
        if transfer_filter is not None:
            transfer_filter.set_selected(
                transaction_type == "transfer"
            )
        pending_filter = getattr(
            self.ids,
            "pending_filter",
            None,
        )
        if pending_filter is not None:
            pending_filter.set_selected(is_pending)


    def render_advanced_filter_state(self):
        state = self.filter_state

        self.ids.account_filter_label.text = state.account_name
        self.ids.group_filter_label.text = state.group_name
        self.ids.category_filter_label.text = state.category_name

        category_enabled = (
            state.group_id is not None
            and state.transaction_type != "transfer"
        )
        self.ids.category_filter.disabled = not category_enabled
        self.ids.category_filter.opacity = (
            1 if category_enabled else .38
        )
        group_enabled = state.transaction_type != "transfer"
        group_filter = getattr(self.ids, "group_filter", None)
        if group_filter is not None:
            group_filter.disabled = not group_enabled
            group_filter.opacity = 1 if group_enabled else .38

        self.ids.start_date_filter_label.text = (
            f"From: {state.start_date.isoformat()}"
            if state.start_date is not None
            else "From Date"
        )
        self.ids.end_date_filter_label.text = (
            f"Through: {state.end_date.isoformat()}"
            if state.end_date is not None
            else "Through Date"
        )

        active_filter_labels = state.active_filter_labels
        self.ids.active_filters_label.text = (
            "Active: " + " • ".join(active_filter_labels)
            if active_filter_labels
            else "No active filters"
        )

        self.ids.reset_all_filters.disabled = not state.is_active
        self.ids.reset_all_filters.opacity = (
            1 if state.is_active else .38
        )


    def set_search_field_text(self, search_text):
        self._suspend_search_refresh = True
        try:
            self.ids.transaction_search.text = search_text
        finally:
            self._suspend_search_refresh = False


    def set_search_text(self, search_text):
        self.filter_state.set_search_text(search_text)

        if self._suspend_search_refresh:
            return

        self.cancel_pending_search_refresh()
        self._search_refresh_event = Clock.schedule_once(
            self.apply_search_text,
            SEARCH_REFRESH_DELAY,
        )


    def apply_search_text(self, *_args):
        self._search_refresh_event = None
        self.render_advanced_filter_state()
        self.load_transactions()


    def cancel_pending_search_refresh(self):
        if self._search_refresh_event is None:
            return

        self._search_refresh_event.cancel()
        self._search_refresh_event = None


    def clear_search(self):
        self.cancel_pending_search_refresh()
        self.filter_state.set_search_text("")
        self.set_search_field_text("")
        self.render_advanced_filter_state()
        self.load_transactions()


    def show_all_transactions(self):
        self.cancel_pending_search_refresh()
        self.filter_state.reset()
        self.render_filter_state()
        self.render_advanced_filter_state()
        self.set_search_field_text("")
        self.load_transactions()


    def open_account_filter_menu(self):
        state = self.filter_state
        menu_items = [
            {
                "text": "All Accounts",
                "selected": state.account_id is None,
                "on_release": lambda:
                    self.select_account_filter(
                        None,
                        "All Accounts",
                    ),
            },
        ]

        for account in get_all_accounts():
            menu_items.append(
                {
                    "text": account.name,
                    "selected": (
                        account.account_id == state.account_id
                    ),
                    "on_release": lambda x=account:
                        self.select_account_filter(
                            x.account_id,
                            x.name,
                        ),
                }
            )

        self.account_filter_menu = EnkryonSelectionPanel(
            title="Filter by Account",
            selected_text=state.account_name,
            options=menu_items,
        )
        self.account_filter_menu.open()


    def select_account_filter(self, account_id, account_name):
        self.filter_state.select_account(
            account_id,
            account_name,
        )
        self.account_filter_menu.dismiss()
        self.refresh_transaction_list()


    def open_group_filter_menu(self):
        state = self.filter_state

        if state.transaction_type == "transfer":
            return

        if state.transaction_type is None:
            groups = get_all_category_groups()
        else:
            groups = get_category_groups_by_type(
                state.transaction_type
            )

        menu_items = [
            {
                "text": "All Category Groups",
                "selected": state.group_id is None,
                "on_release": lambda:
                    self.select_group_filter(
                        None,
                        "All Category Groups",
                    ),
            },
        ]

        for group in groups:
            group_text = group.name
            if state.transaction_type is None:
                group_text = (
                    f"{group.name} "
                    f"({group.transaction_type.title()})"
                )

            menu_items.append(
                {
                    "text": group_text,
                    "selected": group.group_id == state.group_id,
                    "on_release": lambda x=group:
                        self.select_group_filter(
                            x.group_id,
                            x.name,
                        ),
                }
            )

        self.group_filter_menu = EnkryonSelectionPanel(
            title="Filter by Category Group",
            selected_text=state.group_name,
            options=menu_items,
        )
        self.group_filter_menu.open()


    def select_group_filter(self, group_id, group_name):
        self.filter_state.select_group(
            group_id,
            group_name,
        )
        self.group_filter_menu.dismiss()
        self.refresh_transaction_list()


    def open_category_filter_menu(self):
        state = self.filter_state

        if state.group_id is None:
            return

        menu_items = [
            {
                "text": "All Categories",
                "selected": state.category_id is None,
                "on_release": lambda:
                    self.select_category_filter(
                        None,
                        "All Categories",
                    ),
            },
        ]

        for category in get_categories_by_group(state.group_id):
            menu_items.append(
                {
                    "text": category.name,
                    "selected": (
                        category.category_id
                        == state.category_id
                    ),
                    "on_release": lambda x=category:
                        self.select_category_filter(
                            x.category_id,
                            x.name,
                        ),
                }
            )

        self.category_filter_menu = EnkryonSelectionPanel(
            title="Filter by Category",
            selected_text=state.category_name,
            options=menu_items,
        )
        self.category_filter_menu.open()


    def select_category_filter(
        self,
        category_id,
        category_name,
    ):
        state = self.filter_state
        state.select_category(
            category_id,
            category_name,
            state.group_id,
            state.group_name,
            state.transaction_type,
        )
        self.category_filter_menu.dismiss()
        self.refresh_transaction_list()


    def open_start_date_filter(self):
        DatePickerDialog(
            callback=self.set_start_date_filter,
            initial_date=self.filter_state.start_date,
        ).open()


    def open_end_date_filter(self):
        DatePickerDialog(
            callback=self.set_end_date_filter,
            initial_date=self.filter_state.end_date,
        ).open()


    def set_start_date_filter(self, selected_date):
        end_date = self.filter_state.end_date

        if (
            end_date is not None
            and selected_date > end_date
        ):
            end_date = None

        self.filter_state.set_date_range(
            selected_date,
            end_date,
        )
        self.refresh_transaction_list()


    def set_end_date_filter(self, selected_date):
        start_date = self.filter_state.start_date

        if (
            start_date is not None
            and selected_date < start_date
        ):
            start_date = None

        self.filter_state.set_date_range(
            start_date,
            selected_date,
        )
        self.refresh_transaction_list()


    def load_transactions(self):
        activity_list_data = get_activity_list_data(
            **self.filter_state.to_query_arguments(),
        )

        action_text, action_callback = (
            self.get_empty_transaction_action()
        )

        render_transaction_history(
            recycle_view=self.ids.transactions_recycle_view,
            empty_state_container=(
                self.ids.transaction_empty_state_container
            ),
            transactions=activity_list_data["activities"],
            screen=self,
            empty_state=activity_list_data["empty_state"],
            action_text=action_text,
            action_callback=action_callback,
        )


    def refresh_transaction_list(self):
        self.cancel_pending_search_refresh()
        self.render_advanced_filter_state()
        self.load_transactions()


    def on_leave(self):
        self.cancel_pending_search_refresh()
