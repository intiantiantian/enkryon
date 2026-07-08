from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from widgets.transaction_card import TransactionCard

from database.transaction_repository import get_transactions, update_transaction, delete_transaction

class TransactionsScreen(Screen):

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'

    def on_pre_enter(self):
        self.load_transactions()

    def load_transactions(self):
        self.ids.transactions_container.clear_widgets()

        for transaction in get_transactions():
            card = TransactionCard()
            card.screen = self
            card.set_transaction(transaction)
            self.ids.transactions_container.add_widget(card)

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