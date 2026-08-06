from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.uix.card import MDCard

from datetime import datetime

from utils.money import format_signed_money
from utils.transaction_posting import (
    POSTED_STATUS,
    TEMPORARY_STATUS,
)

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

    if transaction_type == "transfer":
        return {
            "label": "TRANSFER",
            "icon": "swap-horizontal",
            "color": hex_to_rgba(Colors.TRANSFER),
        }

    raise ValueError(
        f"Unsupported transaction type: {transaction_type}"
    )


def create_transaction_card_data(transaction, screen):
    record_type = getattr(
        transaction,
        "record_type",
        "transaction",
    )
    transaction_type = getattr(
        transaction,
        "activity_type",
        None,
    )
    if transaction_type is None:
        transaction_type = transaction.transaction_type
    presentation = get_transaction_type_presentation(
        transaction_type
    )
    date_time = datetime.strptime(
        transaction.date_time,
        "%Y-%m-%d %H:%M:%S",
    )

    account_name = transaction.account_name
    group_name = transaction.group_name
    category_name = transaction.category_name
    amount_sign_type = transaction_type
    posting_status = getattr(
        transaction,
        "posting_status",
        POSTED_STATUS,
    )

    if record_type == "transfer":
        account_name = (
            f"{transaction.source_account_name} to "
            f"{transaction.destination_account_name}"
        )
        group_name = "Account Transfer"
        direction = getattr(transaction, "direction", "neutral")
        category_name = {
            "incoming": "Incoming transfer",
            "outgoing": "Outgoing transfer",
        }.get(direction, "Between accounts")
        amount_sign_type = {
            "incoming": "income",
            "outgoing": "expense",
        }.get(direction)
        posting_status = POSTED_STATUS

    is_temporary = posting_status == TEMPORARY_STATUS

    record_id = getattr(transaction, "record_id", None)
    if record_id is None:
        record_id = transaction.transaction_id

    card_data = {
        "transaction_id": record_id,
        "record_type": record_type,
        "screen": screen,
        "account_name": account_name,
        "group_name": group_name,
        "category_name": category_name,
        "amount_text": format_signed_money(
            transaction.amount_centavos,
            amount_sign_type,
            compact=True,
        ),
        "date_time_text": date_time.strftime(
            "%Y-%m-%d %I:%M %p"
        ),
        "transaction_type_icon": presentation["icon"],
        "transaction_type_label": presentation["label"],
        "transaction_type_color": presentation["color"],
        "posting_status": posting_status,
        "is_temporary": is_temporary,
        "posting_status_label": (
            "PENDING" if is_temporary else ""
        ),
        "posting_status_color": hex_to_rgba(Colors.WARNING),
    }
    return card_data


class TransactionCard(MDCard):

    fixed_height = NumericProperty(0)
    transaction_id = ObjectProperty(None, allownone=True)
    record_type = StringProperty("transaction")
    screen = ObjectProperty(None, allownone=True)
    account_name = StringProperty("")
    group_name = StringProperty("")
    category_name = StringProperty("")
    amount_text = StringProperty("")
    date_time_text = StringProperty("")
    transaction_type_icon = StringProperty("")
    transaction_type_label = StringProperty("")
    transaction_type_color = ListProperty([0, 0, 0, 1])
    posting_status = StringProperty(POSTED_STATUS)
    is_temporary = BooleanProperty(False)
    posting_status_label = StringProperty("")
    posting_status_color = ListProperty([0, 0, 0, 1])


    def set_transaction(self, transaction):
        for name, value in create_transaction_card_data(
            transaction,
            self.screen,
        ).items():
            setattr(self, name, value)


    def edit_transaction(self):
        if getattr(self, "record_type", "transaction") == "transfer":
            self.screen.edit_transfer(self.transaction_id)
            return

        self.screen.edit_transaction(self.transaction_id)


    def delete_transaction(self):
        if getattr(self, "record_type", "transaction") == "transfer":
            self.screen.confirm_delete_transfer(
                self.transaction_id
            )
            return

        self.screen.confirm_delete_transaction(
            self.transaction_id,
            getattr(self, "posting_status", POSTED_STATUS),
        )


    def confirm_post_transaction(self):
        if (
            getattr(self, "record_type", "transaction")
            != "transaction"
            or not getattr(self, "is_temporary", False)
        ):
            return

        self.screen.confirm_post_transaction(self.transaction_id)


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
