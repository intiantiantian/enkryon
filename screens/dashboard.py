from kivy.uix.screenmanager import Screen

from database.account_repository import get_all_accounts, get_account_by_id
from database.transaction_repository import (
    get_current_balance_centavos,
    get_total_centavos,
)

from services.transaction_services import (
    get_transaction_list_data,
)

from .transaction_filter_state import TransactionFilterState
from .transaction_list_actions import (
    TransactionListActionsMixin,
)

from widgets.transaction_list import render_transaction_list
from widgets.overlays import EnkryonSelectionPanel

from utils.money import format_money

class DashboardScreen(TransactionListActionsMixin, Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.filter_state = TransactionFilterState()
        self.balance_visible = True


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
        self.filter_state.reset()
        self.ids.account_label.text = (
            self.filter_state.account_name
        )
        self.set_transaction_filter(None)
        self.load_summary()


    def reset_dashboard(self):
        self.filter_state.select_transaction_type(None)
        self.ids.all_filter.set_selected(True)
        self.ids.income_filter.set_selected(False)
        self.ids.expense_filter.set_selected(False)
        self.ids.account_label.text = (
            self.filter_state.account_name
        )


    def load_dashboard(self):
        self.load_summary()
        self.load_recent_transactions()


    def refresh_transaction_list(self):
        self.load_recent_transactions()


    def refresh_after_transaction_delete(self):
        self.load_dashboard()


    def load_summary(self):
        balance_centavos = get_current_balance_centavos(
            self.filter_state.account_id
        )
        income_centavos = get_total_centavos(
            "income",
            self.filter_state.account_id,
        )
        expense_centavos = get_total_centavos(
            "expense",
            self.filter_state.account_id,
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
            **self.filter_state.to_query_arguments(),
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
        self.filter_state.select_account(
            account_id,
            account_name,
        )
        self.ids.account_label.text = (
            self.filter_state.account_name
        )
        self.account_menu.dismiss()
        self.load_dashboard()


    def refresh_selected_account(self):
        state = self.filter_state

        if state.account_id is None:
            self.ids.account_label.text = state.account_name
            return

        account = get_account_by_id(state.account_id)

        if account is None:
            state.clear_account_selection()
            self.ids.account_label.text = state.account_name
            return

        state.select_account(
            account.account_id,
            account.name,
        )
        self.ids.account_label.text = state.account_name


    def toggle_balance(self):
        self.balance_visible = not self.balance_visible
        self.load_summary()
