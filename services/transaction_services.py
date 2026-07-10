from database.transaction_repository import delete_transaction, get_transactions
from utils.snackbar import show_snackbar
from widgets.transaction_card import TransactionCard

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

def load_transactions(self, limit=None):
        self.ids.transactions_container.clear_widgets()

        for transaction in get_transactions(transaction_type=self.transaction_filter, limit=limit):
            card = TransactionCard()
            card.screen = self
            card.set_transaction(transaction)
            self.ids.transactions_container.add_widget(card)
            
def perform_delete_transaction(self, transaction_id, dialog_screen):
    close_delete_transaction_dialog(dialog_screen)
    delete_transaction(transaction_id)
    load_transactions(self)
    show_snackbar("Transaction deleted successfully.")

def close_delete_transaction_dialog(dialog_screen):
    dialog_screen.dismiss()