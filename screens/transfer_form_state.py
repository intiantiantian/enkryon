from dataclasses import dataclass

from database.records import TransferRecord
from utils.money import centavos_to_peso_text
from utils.transaction_datetime import split_database_datetime


SOURCE_ACCOUNT_PROMPT = "Select Source Account"
DESTINATION_ACCOUNT_PROMPT = "Select Destination Account"
INTERNAL_TRANSFER_KIND = "internal"
PASS_THROUGH_TRANSFER_KIND = "pass_through"


@dataclass
class TransferFormState:
    amount: str = "0"
    source_account_id: int | None = None
    source_account_name: str = SOURCE_ACCOUNT_PROMPT
    destination_account_id: int | None = None
    destination_account_name: str = DESTINATION_ACCOUNT_PROMPT
    date_label: str = ""
    time_label: str = ""
    notes: str = ""
    transfer_id: int | None = None
    transfer_kind: str = INTERNAL_TRANSFER_KIND
    counterparty: str = ""


    @classmethod
    def empty(cls, date_label, time_label):
        return cls(
            date_label=date_label,
            time_label=time_label,
        )


    @classmethod
    def from_transfer(cls, transfer: TransferRecord):
        date_label, time_label = split_database_datetime(
            transfer.date_time
        )

        return cls(
            amount=centavos_to_peso_text(transfer.amount_centavos),
            source_account_id=transfer.source_account_id,
            source_account_name=transfer.source_account_name,
            destination_account_id=transfer.destination_account_id,
            destination_account_name=transfer.destination_account_name,
            date_label=date_label,
            time_label=time_label,
            notes=transfer.notes or "",
            transfer_id=transfer.transfer_id,
            transfer_kind=transfer.transfer_kind,
            counterparty=transfer.counterparty or "",
        )


    def to_save_arguments(self):
        return {
            "source_account_id": self.source_account_id,
            "destination_account_id": self.destination_account_id,
            "amount": self.amount,
            "date_label": self.date_label,
            "time_label": self.time_label,
            "notes_label": self.notes,
            "transfer_id": self.transfer_id,
            "transfer_kind": self.transfer_kind,
            "counterparty": self.counterparty,
        }


    def select_source_account(self, account_id, account_name):
        self.source_account_id = account_id
        self.source_account_name = account_name


    def clear_source_account_selection(self):
        self.source_account_id = None
        self.source_account_name = SOURCE_ACCOUNT_PROMPT


    def select_destination_account(self, account_id, account_name):
        self.destination_account_id = account_id
        self.destination_account_name = account_name


    def clear_destination_account_selection(self):
        self.destination_account_id = None
        self.destination_account_name = DESTINATION_ACCOUNT_PROMPT


    def set_notes(self, notes):
        self.notes = notes if notes and notes.strip() else ""


    def set_transfer_kind(self, transfer_kind):
        if transfer_kind not in {
            INTERNAL_TRANSFER_KIND,
            PASS_THROUGH_TRANSFER_KIND,
        }:
            raise ValueError(f"Unknown transfer kind: {transfer_kind}")
        self.transfer_kind = transfer_kind


    def set_counterparty(self, counterparty):
        self.counterparty = counterparty or ""
