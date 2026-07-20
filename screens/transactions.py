from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from .transaction_list_actions import TransactionListActionsMixin

from services.transaction_services import (
    delete_transaction_by_id,
    get_transaction_list_data,
)

from widgets.transaction_list import render_transaction_list

class TransactionsScreen(TransactionListActionsMixin, Screen):

    transaction_filter = None

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'


    def on_pre_enter(self):
        self.ids.all_filter.set_selected(self.transaction_filter == None)
        self.ids.income_filter.set_selected(self.transaction_filter == "income")
        self.ids.expense_filter.set_selected(self.transaction_filter == "expense")
        self.transaction_filter = None

        self.load_transactions()


    def load_transactions(self):
        transaction_list_data = get_transaction_list_data(
            account_id=getattr(self, "selected_account_id", None),
            transaction_filter=self.transaction_filter,
        )

        render_transaction_list(
            container=self.ids.transactions_container,
            transactions=transaction_list_data["transactions"],
            screen=self,
            empty_state=transaction_list_data["empty_state"],
        )


    def refresh_transaction_list(self):
        self.load_transactions()
