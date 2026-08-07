from dataclasses import dataclass
from datetime import date

from utils.transaction_posting import (
    POSTED_STATUS,
    TEMPORARY_STATUS,
)


TRANSFER_KINDS = {"internal", "pass_through"}


@dataclass
class TransactionFilterState:
    search_text: str = ""
    transaction_type: str | None = None
    posting_status: str | None = None
    transfer_kind: str | None = None
    account_id: int | None = None
    account_name: str = "All Accounts"
    group_id: int | None = None
    group_name: str = "All Category Groups"
    category_id: int | None = None
    category_name: str = "All Categories"
    start_date: date | None = None
    end_date: date | None = None


    def __post_init__(self):
        self.set_search_text(self.search_text)
        if self.transfer_kind is not None:
            if self.transfer_kind not in TRANSFER_KINDS:
                raise ValueError("Unsupported transfer kind.")
            self.transaction_type = "transfer"
            self.posting_status = None
        elif (
            self.posting_status is None
            and self.transaction_type in {"income", "expense"}
        ):
            self.posting_status = POSTED_STATUS
        self.set_date_range(self.start_date, self.end_date)


    @property
    def is_active(self):
        return any(
            (
                self.search_text,
                self.transaction_type,
                self.posting_status,
                self.transfer_kind,
                self.account_id is not None,
                self.group_id is not None,
                self.category_id is not None,
                self.start_date is not None,
                self.end_date is not None,
            )
        )


    @property
    def active_filter_labels(self):
        labels = []

        if self.search_text:
            labels.append(f'Search: "{self.search_text}"')

        if self.posting_status == TEMPORARY_STATUS:
            labels.append("Pending")

        if self.transaction_type is not None:
            if (
                self.transaction_type == "transfer"
                and self.transfer_kind is not None
            ):
                transfer_kind_label = {
                    "internal": "Internal",
                    "pass_through": "Pass-through",
                }[self.transfer_kind]
                labels.append(f"Transfer: {transfer_kind_label}")
            else:
                labels.append(self.transaction_type.title())

        if self.account_id is not None:
            labels.append(f"Account: {self.account_name}")

        if self.group_id is not None:
            labels.append(f"Group: {self.group_name}")

        if self.category_id is not None:
            labels.append(f"Category: {self.category_name}")

        if self.start_date is not None:
            labels.append(
                f"From: {self.start_date.isoformat()}"
            )

        if self.end_date is not None:
            labels.append(
                f"Through: {self.end_date.isoformat()}"
            )

        return labels


    @property
    def activity_type(self):
        return self.transaction_type


    @activity_type.setter
    def activity_type(self, value):
        self.transaction_type = value


    def to_query_arguments(self):
        return {
            "search_text": self.search_text or None,
            "account_id": self.account_id,
            "activity_type": self.transaction_type,
            "posting_status": self.posting_status,
            "transfer_kind": self.transfer_kind,
            "group_id": self.group_id,
            "category_id": self.category_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
        }


    def set_search_text(self, search_text):
        self.search_text = (search_text or "").strip()


    def select_account(self, account_id, account_name):
        self.account_id = account_id
        self.account_name = account_name


    def clear_account_selection(self):
        self.account_id = None
        self.account_name = "All Accounts"


    def select_activity_filter(self, activity_filter):
        if activity_filter == "pending":
            transaction_type = None
            posting_status = TEMPORARY_STATUS
        else:
            transaction_type = activity_filter
            posting_status = (
                POSTED_STATUS
                if activity_filter in {"income", "expense"}
                else None
            )

        if (
            transaction_type != self.transaction_type
            or posting_status != self.posting_status
            or self.transfer_kind is not None
        ):
            self.clear_group_selection()

        self.transaction_type = transaction_type
        self.posting_status = posting_status
        self.transfer_kind = None


    def select_transfer_kind(self, transfer_kind):
        if transfer_kind not in TRANSFER_KINDS:
            raise ValueError("Unsupported transfer kind.")

        if (
            self.transaction_type != "transfer"
            or self.transfer_kind != transfer_kind
        ):
            self.clear_group_selection()

        self.transaction_type = "transfer"
        self.posting_status = None
        self.transfer_kind = transfer_kind


    def select_transaction_type(self, transaction_type):
        self.select_activity_filter(transaction_type)


    def select_group(
        self,
        group_id,
        group_name,
        transaction_type=None,
    ):
        if group_id != self.group_id:
            self.clear_category_selection()

        if transaction_type is not None:
            self.transaction_type = transaction_type
            self.transfer_kind = None
        self.group_id = group_id
        self.group_name = group_name


    def clear_group_selection(self):
        self.group_id = None
        self.group_name = "All Category Groups"
        self.clear_category_selection()


    def select_category(
        self,
        category_id,
        category_name,
        group_id,
        group_name,
        transaction_type,
    ):
        self.transaction_type = transaction_type
        self.transfer_kind = None
        self.group_id = group_id
        self.group_name = group_name
        self.category_id = category_id
        self.category_name = category_name


    def clear_category_selection(self):
        self.category_id = None
        self.category_name = "All Categories"


    def set_date_range(self, start_date, end_date):
        if (
            start_date is not None
            and end_date is not None
            and start_date > end_date
        ):
            raise ValueError(
                "Start date cannot be after end date."
            )

        self.start_date = start_date
        self.end_date = end_date


    def reset(self):
        self.search_text = ""
        self.transaction_type = None
        self.posting_status = None
        self.transfer_kind = None
        self.clear_account_selection()
        self.clear_group_selection()
        self.start_date = None
        self.end_date = None
