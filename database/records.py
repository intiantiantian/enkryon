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
    posting_status: str = "posted"


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
    posting_status: str = "posted"


class TransferRecord(NamedTuple):
    transfer_id: int
    source_account_id: int
    destination_account_id: int
    amount_centavos: int
    date_time: str
    notes: str | None
    source_account_name: str
    destination_account_name: str
    transfer_kind: str = "internal"
    counterparty: str | None = None


class InterestProfileRecord(NamedTuple):
    profile_id: int
    account_id: int
    annual_rate_micros: int
    day_count_basis: int
    effective_from: str
    enabled: bool


class InterestAccrualRecord(NamedTuple):
    accrual_id: int
    account_id: int
    interest_profile_id: int
    accrual_date: str
    closing_balance_centavos: int
    annual_rate_micros: int
    day_count_basis: int
    accrued_whole_centavos: int
    accrued_remainder_numerator: int
    status: str
    posted_transaction_id: int | None


class ActivityRecord(NamedTuple):
    record_id: int
    record_type: str
    account_name: str
    group_name: str
    category_name: str
    amount_centavos: int
    date_time: str
    notes: str | None
    activity_type: str
    source_account_id: int | None
    destination_account_id: int | None
    source_account_name: str | None
    destination_account_name: str | None
    direction: str
    posting_status: str = "posted"
    transfer_kind: str | None = None
    counterparty: str | None = None

    @property
    def transaction_id(self):
        return self.record_id

    @property
    def transaction_type(self):
        return self.activity_type
