from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from services.transaction_services import (
    delete_transaction_by_id,
    get_transaction_list_data,
)

from widgets.transaction_list import render_transaction_list

from utils.snackbar import show_snackbar

class TransactionsScreen(Screen):

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

    def set_transaction_filter(self, transaction_type):
        self.transaction_filter = transaction_type

        self.ids.all_filter.set_selected(transaction_type == None)
        self.ids.income_filter.set_selected(transaction_type == "income")
        self.ids.expense_filter.set_selected(transaction_type == "expense")
        
        self.load_transactions()

    def edit_transaction(self, transaction_id):
        screen = self.manager.get_screen('add_transaction')
        screen.load_transaction(transaction_id)
        self.manager.current = 'add_transaction'

    def delete_transaction(self, transaction_id):
        result = delete_transaction_by_id(transaction_id)
        self.delete_transaction_dialog.dismiss()

        show_snackbar(result.message)

        if not result.success:
            return

        self.load_transactions()

    def confirm_delete_transaction(self, transaction_id):
        self.delete_transaction_dialog = MDDialog(
            title="Confirm Delete",
            text="Are you sure you want to delete this transaction?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.delete_transaction_dialog.dismiss()
                ),
                MDFlatButton(
                    text="DELETE",
                    on_release=lambda x: self.delete_transaction(transaction_id)
                )
            ]
        )
        self.delete_transaction_dialog.open()
