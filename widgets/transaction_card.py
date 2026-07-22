from kivymd.uix.card import MDCard

from datetime import datetime

from utils.money import format_signed_money

from widgets.empty_state import EmptyState

from theme.tokens import Colors, hex_to_rgba


def get_transaction_type_presentation(transaction_type):
    if transaction_type == "income":
        return {
            "label": "INCOME",
            "icon": "arrow-up",
            "color": hex_to_rgba(Colors.INCOME),
        }

    if transaction_type == "expense":
        return {
            "label": "EXPENSE",
            "icon": "arrow-down",
            "color": hex_to_rgba(Colors.EXPENSE),
        }

    raise ValueError(
        f"Unsupported transaction type: {transaction_type}"
    )

class TransactionCard(MDCard):


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transaction_id = None


    def set_transaction(self, transaction):
        self.transaction_id = transaction.transaction_id

        self.ids.account_name.text = transaction.account_name
        self.ids.group_name.text = transaction.group_name
        self.ids.category_name.text = transaction.category_name

        amount_centavos = transaction.amount_centavos
        transaction_type = transaction.transaction_type
        presentation = get_transaction_type_presentation(
            transaction_type
        )

        self.ids.amount.text = format_signed_money(
            amount_centavos,
            transaction_type,
            compact=True
        )

        self.ids.amount.text_color = presentation["color"]

        dt = datetime.strptime(
            transaction.date_time,
            "%Y-%m-%d %H:%M:%S",
        )
        self.ids.date_time.text = dt.strftime(
            "%Y-%m-%d %I:%M %p"
        )

        self.ids.transaction_type_icon.icon = presentation["icon"]
        self.ids.transaction_type_icon.text_color = (
            presentation["color"]
        )
        self.ids.transaction_type.text = presentation["label"]
        self.ids.transaction_type.text_color = presentation["color"]


    def edit_transaction(self):
        self.screen.edit_transaction(self.transaction_id)


    def delete_transaction(self):
        self.screen.confirm_delete_transaction(self.transaction_id)


def create_transaction_empty_state(
    empty_state,
    *,
    action_text="",
    action_callback=None,
):
    return EmptyState(
        icon="receipt-text-outline",
        title=empty_state["title"],
        message=empty_state["message"],
        action_text=action_text,
        action_callback=action_callback,
    )

def create_transaction_card(transaction, screen):
    card = TransactionCard()
    card.screen = screen
    card.set_transaction(transaction)
    return card
