from kivy.uix.screenmanager import Screen

from .transaction_list_actions import TransactionListActionsMixin

from services.transaction_services import (
    get_transaction_list_data,
)

from widgets.transaction_list import render_transaction_list

class TransactionsScreen(TransactionListActionsMixin, Screen):

    transaction_filter = None

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'


    def go_to_add_transaction(self):
        self.manager.current = "add_transaction"


    def on_pre_enter(self):
        self.ids.all_filter.set_selected(self.transaction_filter == None)
        self.ids.income_filter.set_selected(self.transaction_filter == "income")
        self.ids.expense_filter.set_selected(self.transaction_filter == "expense")
        self.transaction_filter = None

        self.load_transactions()


    def load_transactions(self):
        transaction_list_data = get_transaction_list_data(
            account_id=getattr(self, "selected_account_id", None),
            transaction_type=self.transaction_filter,
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
        self.load_transactions()
