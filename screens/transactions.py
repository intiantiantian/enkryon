from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.utils import get_color_from_hex

from widgets.transaction_card import TransactionCard

from database.transaction_repository import get_transactions, delete_transaction

class TransactionsScreen(Screen):

    transaction_filter = None

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'

    def on_pre_enter(self):
        self.ids.all_filter.md_bg_color = get_color_from_hex('#D5F4BE')
        self.ids.income_filter.md_bg_color = get_color_from_hex("#FFFFFF")
        self.ids.expense_filter.md_bg_color = get_color_from_hex("#FFFFFF")
        self.transaction_filter = None

        self.load_transactions()

    def load_transactions(self):
        self.ids.transactions_container.clear_widgets()

        for transaction in get_transactions(transaction_type=self.transaction_filter):
            card = TransactionCard()
            card.screen = self
            card.set_transaction(transaction)
            self.ids.transactions_container.add_widget(card)

    def set_transaction_filter(self, transaction_type):
        self.transaction_filter = transaction_type

        active = get_color_from_hex('#D5F4BE')
        inactive = get_color_from_hex("#FFFFFF")

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

    def perform_delete_transaction(self, transaction_id):
        self.close_delete_transaction_dialog()
        delete_transaction(transaction_id)
        print(f"Transaction with ID '{transaction_id}' deleted successfully.")
        self.load_transactions()

    def confirm_delete_transaction(self, transaction_id):
        self.delete_transaction_dialog = MDDialog(
            title="Confirm Delete",
            text="Are you sure you want to delete this transaction?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=self.close_delete_transaction_dialog
                ),
                MDFlatButton(
                    text="DELETE",
                    on_release=lambda x: self.perform_delete_transaction(transaction_id)
                )
            ]
        )
        self.delete_transaction_dialog.open()

    def close_delete_transaction_dialog(self, *args):
        self.delete_transaction_dialog.dismiss()