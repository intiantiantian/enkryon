from kivy.properties import (
    ListProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.recycleview.views import RecycleDataViewBehavior
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


def create_transaction_card_data(transaction, screen):
    presentation = get_transaction_type_presentation(
        transaction.transaction_type
    )
    date_time = datetime.strptime(
        transaction.date_time,
        "%Y-%m-%d %H:%M:%S",
    )

    return {
        "transaction_id": transaction.transaction_id,
        "screen": screen,
        "account_name": transaction.account_name,
        "group_name": transaction.group_name,
        "category_name": transaction.category_name,
        "amount_text": format_signed_money(
            transaction.amount_centavos,
            transaction.transaction_type,
            compact=True,
        ),
        "date_time_text": date_time.strftime(
            "%Y-%m-%d %I:%M %p"
        ),
        "transaction_type_icon": presentation["icon"],
        "transaction_type_label": presentation["label"],
        "transaction_type_color": presentation["color"],
    }


class TransactionCard(MDCard):

    transaction_id = ObjectProperty(None, allownone=True)
    screen = ObjectProperty(None, allownone=True)
    account_name = StringProperty("")
    group_name = StringProperty("")
    category_name = StringProperty("")
    amount_text = StringProperty("")
    date_time_text = StringProperty("")
    transaction_type_icon = StringProperty("")
    transaction_type_label = StringProperty("")
    transaction_type_color = ListProperty([0, 0, 0, 1])


    def set_transaction(self, transaction):
        for name, value in create_transaction_card_data(
            transaction,
            self.screen,
        ).items():
            setattr(self, name, value)


    def edit_transaction(self):
        self.screen.edit_transaction(self.transaction_id)


    def delete_transaction(self):
        self.screen.confirm_delete_transaction(self.transaction_id)


class TransactionHistoryCard(
    RecycleDataViewBehavior,
    TransactionCard,
):
    pass


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
