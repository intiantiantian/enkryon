from typing import NamedTuple


class AccountRecord(NamedTuple):
    account_id: int
    name: str


class CategoryGroupRecord(NamedTuple):
    group_id: int
    name: str
    transaction_type: str


class CategoryRecord(NamedTuple):
    category_id: int
    group_id: int
    name: str
    group_name: str
    transaction_type: str


class TransactionListRecord(NamedTuple):
    transaction_id: int
    account_name: str
    group_name: str
    category_name: str
    amount_centavos: int
    date_time: str
    notes: str | None
    transaction_type: str


class TransactionDetailRecord(NamedTuple):
    transaction_id: int
    account_id: int
    amount_centavos: int
    category_id: int
    date_time: str
    notes: str | None
    account_name: str
    category_name: str
    group_id: int
    group_name: str
    transaction_type: str


class TransferRecord(NamedTuple):
    transfer_id: int
    source_account_id: int
    destination_account_id: int
    amount_centavos: int
    date_time: str
    notes: str | None
    source_account_name: str
    destination_account_name: str
