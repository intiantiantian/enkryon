from database.transaction_repository import delete_transaction, get_transactions
from utils.snackbar import show_snackbar
from widgets.transaction_card import TransactionCard

def load_transactions(screen, limit=None):
    screen.ids.transactions_container.clear_widgets()

    account_id = getattr(screen, "selected_account_id", None)

    for transaction in get_transactions(
        account_id=account_id,
        transaction_type=screen.transaction_filter,
        limit=limit
    ):
        card = TransactionCard()
        card.screen = screen
        card.set_transaction(transaction)
        screen.ids.transactions_container.add_widget(card)
            
def perform_delete_transaction(self, transaction_id, dialog_screen):
    delete_transaction(transaction_id)
    close_delete_transaction_dialog(dialog_screen)
    self.load_dashboard()
    show_snackbar("Transaction deleted successfully.")

def close_delete_transaction_dialog(dialog_screen):
    dialog_screen.dismiss()