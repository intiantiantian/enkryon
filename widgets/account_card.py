from kivy.properties import StringProperty
from kivymd.uix.card import MDCard


class AccountCard(MDCard):
    interest_summary_text = StringProperty("Interest: Not configured")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.account_id = None

    def set_account(self, account):
        self.ids.account_name.text = account.name
        self.account_id = account.account_id

    def set_interest_summary(self, summary_text):
        self.interest_summary_text = summary_text

    def edit_account(self):
        self.screen.open_rename_dialog(
            self.account_id,
            self.ids.account_name.text,
        )

    def manage_interest(self):
        self.screen.open_interest_dialog(
            self.account_id,
            self.ids.account_name.text,
        )

    def delete_account(self):
        self.screen.confirm_delete_account(self.account_id)
