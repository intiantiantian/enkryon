from dataclasses import dataclass
from datetime import date


@dataclass
class TransactionFilterState:
    search_text: str = ""
    transaction_type: str | None = None
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
        self.set_date_range(self.start_date, self.end_date)


    @property
    def is_active(self):
        return any(
            (
                self.search_text,
                self.transaction_type,
                self.account_id is not None,
                self.group_id is not None,
                self.category_id is not None,
                self.start_date is not None,
                self.end_date is not None,
            )
        )


    def to_query_arguments(self):
        return {
            "search_text": self.search_text or None,
            "account_id": self.account_id,
            "transaction_type": self.transaction_type,
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


    def select_transaction_type(self, transaction_type):
        if transaction_type != self.transaction_type:
            self.clear_group_selection()

        self.transaction_type = transaction_type


    def select_group(
        self,
        group_id,
        group_name,
        transaction_type,
    ):
        if group_id != self.group_id:
            self.clear_category_selection()

        self.transaction_type = transaction_type
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
        self.clear_account_selection()
        self.clear_group_selection()
        self.start_date = None
        self.end_date = None
