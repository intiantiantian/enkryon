from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

from .transaction_filter_state import TransactionFilterState
from .transaction_list_actions import TransactionListActionsMixin

from services.transaction_services import (
    get_transaction_list_data,
)

from widgets.transaction_list import render_transaction_list


SEARCH_REFRESH_DELAY = 0.25

class TransactionsScreen(TransactionListActionsMixin, Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.filter_state = TransactionFilterState()
        self._search_refresh_event = None
        self._suspend_search_refresh = False


    def go_to_dashboard(self):
        self.manager.current = 'dashboard'


    def go_to_add_transaction(self):
        self.manager.current = "add_transaction"


    def on_pre_enter(self):
        self.cancel_pending_search_refresh()
        self.filter_state.reset()
        self.render_filter_state()
        self.set_search_field_text("")
        self.load_transactions()


    def render_filter_state(self):
        transaction_type = self.filter_state.transaction_type

        self.ids.all_filter.set_selected(
            transaction_type is None
        )
        self.ids.income_filter.set_selected(
            transaction_type == "income"
        )
        self.ids.expense_filter.set_selected(
            transaction_type == "expense"
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
        self.load_transactions()


    def show_all_transactions(self):
        self.cancel_pending_search_refresh()
        self.filter_state.reset()
        self.render_filter_state()
        self.set_search_field_text("")
        self.load_transactions()


    def load_transactions(self):
        transaction_list_data = get_transaction_list_data(
            **self.filter_state.to_query_arguments(),
        )

        action_text, action_callback = (
            self.get_empty_transaction_action()
        )

        render_transaction_list(
            container=self.ids.transactions_container,
            transactions=transaction_list_data["transactions"],
            screen=self,
            empty_state=transaction_list_data["empty_state"],
            action_text=action_text,
            action_callback=action_callback,
        )


    def refresh_transaction_list(self):
        self.cancel_pending_search_refresh()
        self.load_transactions()


    def on_leave(self):
        self.cancel_pending_search_refresh()
