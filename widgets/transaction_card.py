from kivymd.uix.card import MDCard

from datetime import datetime

from utils.money import format_signed_money

from widgets.empty_state import EmptyState

class TransactionCard(MDCard):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transaction_id = None

    def set_transaction(self, transaction):
        self.transaction_id = transaction[0]

        self.ids.account_name.text = transaction[1]
        self.ids.group_name.text = transaction[2]
        self.ids.category_name.text = transaction[3]

        amount_centavos = transaction[4]
        transaction_type = transaction[7]

        self.ids.amount.text = format_signed_money(
            amount_centavos,
            transaction_type,
            compact=True
        )

        dt = datetime.strptime(transaction[5], "%Y-%m-%d %H:%M:%S")
        self.ids.date_time.text = dt.strftime("%Y-%m-%d %I:%M %p")

        self.ids.transaction_type.text = transaction[7].upper()

    def edit_transaction(self):
        self.screen.edit_transaction(self.transaction_id)

    def delete_transaction(self):
        self.screen.confirm_delete_transaction(self.transaction_id)

def create_transaction_empty_state(empty_state):
    return EmptyState(
        title=empty_state["title"],
        message=empty_state["message"]
    )

def create_transaction_card(transaction, screen):
    card = TransactionCard()
    card.screen = screen
    card.set_transaction(transaction)
    return card