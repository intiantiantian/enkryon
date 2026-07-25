from kivy.uix.screenmanager import Screen

from database.account_repository import get_all_accounts, get_account_by_id
from database.transaction_repository import (
    get_current_balance_centavos,
    get_total_centavos,
)

from services.transaction_services import (
    get_transaction_list_data,
)

from .transaction_list_actions import (
    TransactionListActionsMixin,
)

from widgets.transaction_list import render_transaction_list
from widgets.overlays import EnkryonSelectionPanel

from utils.money import format_money

class DashboardScreen(TransactionListActionsMixin, Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selected_account_id = None
        self.balance_visible = True
        self.transaction_filter = None


    def on_pre_enter(self):
        self.refresh_selected_account()
        self.reset_dashboard()
        self.load_dashboard()


    def go_to_add_transaction(self):
        self.manager.current = 'add_transaction'


    def go_to_settings(self):
        self.manager.current = 'settings'


    def go_to_accounts(self):
        self.manager.current = 'accounts'


    def go_to_categories(self):
        self.manager.current = 'categories'


    def go_to_transactions(self):
        self.manager.current = 'transactions'


    def show_all_transactions(self):
        self.selected_account_id = None
        self.ids.account_label.text = "All Accounts"
        self.set_transaction_filter(None)
        self.load_summary()


    def reset_dashboard(self):
        self.ids.all_filter.set_selected(self.transaction_filter == None)
        self.ids.income_filter.set_selected(self.transaction_filter == "income")
        self.ids.expense_filter.set_selected(self.transaction_filter == "expense")
        self.transaction_filter = None

        if self.selected_account_id is None:
            self.ids.account_label.text = 'All Accounts'


    def load_dashboard(self):
        self.load_summary()
        self.load_recent_transactions()


    def refresh_transaction_list(self):
        self.load_recent_transactions()


    def refresh_after_transaction_delete(self):
        self.load_dashboard()


    def load_summary(self):
        balance_centavos = get_current_balance_centavos(
            self.selected_account_id
        )
        income_centavos = get_total_centavos(
            "income",
            self.selected_account_id,
        )
        expense_centavos = get_total_centavos(
            "expense",
            self.selected_account_id,
        )

        if self.balance_visible:
            self.ids.balance_label.text = format_money(
                balance_centavos,
                compact=True,
            )
            self.ids.income_label.text = format_money(
                income_centavos,
                compact=True,
            )
            self.ids.expense_label.text = format_money(
                expense_centavos,
                compact=True,
            )
            self.ids.eye_button.icon = "eye"
        else:
            self.ids.balance_label.text = "₱ ******"
            self.ids.income_label.text = "₱ ******"
            self.ids.expense_label.text = "₱ ******"
            self.ids.eye_button.icon = "eye-off"


    def load_recent_transactions(self):
        transaction_list_data = get_transaction_list_data(
            account_id=getattr(self, "selected_account_id", None),
            transaction_type=self.transaction_filter,
            limit=3,
            compact_empty_state=True,
        )
        action_text, action_callback = (
            self.get_empty_transaction_action()
        )
        render_transaction_list(
            container=self.ids.transactions_container,
            transactions=transaction_list_data["transactions"],
            screen=self,
            empty_state=transaction_list_data["empty_state"],
            action_text=action_text,
            action_callback=action_callback,
        )


    def open_account_menu(self):
        accounts = get_all_accounts()
        if not accounts:
            self.ids.account_label.text = 'No Accounts'
            return

        menu_items = []

        menu_items.append(
            {
                "text": "All Accounts",
                "on_release": lambda: self.select_account(None, "All Accounts")
            }
        )

        for account in accounts:
            menu_items.append(
                {
                    "text": account.name,
                    "on_release": lambda x=account:
                        self.select_account(
                            x.account_id,
                            x.name,
                        )
                }
            )

        self.account_menu = EnkryonSelectionPanel(
            title="Filter by Account",
            selected_text=self.ids.account_label.text,
            options=menu_items,
        )

        self.account_menu.open()


    def select_account(self, account_id, account_name):
        self.ids.account_label.text = account_name
        self.selected_account_id = account_id
        self.account_menu.dismiss()
        self.load_dashboard()


    def refresh_selected_account(self):
        if self.selected_account_id is None:
            self.ids.account_label.text = "All Accounts"
            return

        account = get_account_by_id(self.selected_account_id)

        if account is None:
            self.selected_account_id = None
            self.ids.account_label.text = "All Accounts"
            return

        self.ids.account_label.text = account.name


    def toggle_balance(self):
        self.balance_visible = not self.balance_visible
        self.load_summary()
