from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.utils import get_color_from_hex

from services.transaction_services import (
    delete_transaction_by_id,
    get_transaction_list_data,
)

from widgets.transaction_list import render_transaction_list

from theme.widget_states import SELECTED_BUTTON_BG, UNSELECTED_BUTTON_BG

from utils.snackbar import show_snackbar

class TransactionsScreen(Screen):

    transaction_filter = None

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'

    def on_pre_enter(self):
        self.ids.all_filter.md_bg_color = SELECTED_BUTTON_BG
        self.ids.income_filter.md_bg_color = UNSELECTED_BUTTON_BG
        self.ids.expense_filter.md_bg_color = UNSELECTED_BUTTON_BG
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

        active = SELECTED_BUTTON_BG
        inactive = UNSELECTED_BUTTON_BG

        self.ids.all_filter.md_bg_color = (
            active if transaction_type is None else inactive
        )

        self.ids.income_filter.md_bg_color = (
            active if transaction_type == 'income' else inactive
        )

        self.ids.expense_filter.md_bg_color = (
            active if transaction_type == 'expense' else inactive
        )
        
        self.load_transactions()

    def edit_transaction(self, transaction_id):
        screen = self.manager.get_screen('add_transaction')
        screen.load_transaction(transaction_id)
        self.manager.current = 'add_transaction'

    def delete_transaction(self, transaction_id):
        delete_transaction_by_id(transaction_id)
        self.delete_transaction_dialog.dismiss()
        self.load_transactions()
        show_snackbar("Transaction deleted successfully.")

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