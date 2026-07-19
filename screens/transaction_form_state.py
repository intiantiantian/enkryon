from dataclasses import dataclass

from database.records import TransactionDetailRecord
from utils.money import centavos_to_peso_text
from utils.transaction_datetime import split_database_datetime


@dataclass
class TransactionFormState:
    amount: str = "0"
    transaction_type: str | None = None
    account_id: int | None = None
    account_name: str = "Select Account"
    group_id: int | None = None
    group_name: str = "No Transaction Type Selected"
    category_id: int | None = None
    category_name: str = "No Category Group Selected"
    date_label: str = ""
    time_label: str = ""
    notes: str = ""
    transaction_id: int | None = None

    @classmethod
    def empty(cls, date_label, time_label):
        return cls(
            date_label=date_label,
            time_label=time_label,
        )

    @classmethod
    def from_transaction(cls, transaction: TransactionDetailRecord):
        date_label, time_label = split_database_datetime(
            transaction.date_time
        )

        return cls(
            amount=centavos_to_peso_text(transaction.amount_centavos),
            transaction_type=transaction.transaction_type,
            account_id=transaction.account_id,
            account_name=transaction.account_name,
            group_id=transaction.group_id,
            group_name=transaction.group_name,
            category_id=transaction.category_id,
            category_name=transaction.category_name,
            date_label=date_label,
            time_label=time_label,
            notes=transaction.notes or "",
            transaction_id=transaction.transaction_id,
        )

    def to_save_arguments(self):
        return {
            "account_id": self.account_id,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "category_id": self.category_id,
            "date_label": self.date_label,
            "time_label": self.time_label,
            "notes_label": self.notes,
            "transaction_id": self.transaction_id,
        }
