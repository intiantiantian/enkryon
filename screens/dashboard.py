from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.utils import get_color_from_hex

from database.account_repository import get_all_accounts
from database.transaction_repository import (
    get_total_amount,
    get_current_balance,
)

from services.transaction_services import close_delete_transaction_dialog, load_transactions, perform_delete_transaction

from utils.money import format_money

class DashboardScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selected_account_id = None
        self.balance_visible = True
        self.transaction_filter = None
        self.first_load = True

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

    def on_pre_enter(self):
        self.reset_dashboard()

        if self.first_load:
            self.load_dashboard()
            self.first_load = False

    def reset_dashboard(self):
        self.ids.all_filter.md_bg_color = get_color_from_hex('#D5F4BE')
        self.ids.income_filter.md_bg_color = get_color_from_hex("#FFFFFF")
        self.ids.expense_filter.md_bg_color = get_color_from_hex("#FFFFFF")
        self.transaction_filter = None

        if self.selected_account_id is None:
            self.ids.account_label.text = 'All Accounts'

    def load_dashboard(self):
        self.load_summary()
        self.load_recent_transactions()

    def load_summary(self):
        balance = get_current_balance(self.selected_account_id)
        income = get_total_amount('income', self.selected_account_id)
        expense = get_total_amount('expense', self.selected_account_id)

        if self.balance_visible:
            self.ids.balance_label.text = format_money(balance, compact=True)
            self.ids.income_label.text = format_money(income, compact=True)
            self.ids.expense_label.text = format_money(expense, compact=True)
            self.ids.eye_button.icon = "eye"
        else:
            self.ids.balance_label.text = "₱ ******"
            self.ids.income_label.text = "₱ ******"
            self.ids.expense_label.text = "₱ ******"
            self.ids.eye_button.icon = "eye-off"

    def load_recent_transactions(self):
        load_transactions(self, limit=5)

    def set_transaction_filter(self, transaction_type):
        self.transaction_filter = transaction_type

        active = get_color_from_hex('#D5F4BE')
        inactive = get_color_from_hex("#FFFFFF")

        self.ids.all_filter.md_bg_color = (
            active if transaction_type is None else inactive
        )

        self.ids.income_filter.md_bg_color = (
            active if transaction_type == 'income' else inactive
        )

        self.ids.expense_filter.md_bg_color = (
            active if transaction_type == 'expense' else inactive
        )
        
        self.load_recent_transactions()

    def edit_transaction(self, transaction_id):
        screen = self.manager.get_screen('add_transaction')
        screen.load_transaction(transaction_id)
        self.manager.current = 'add_transaction'

    def confirm_delete_transaction(self, transaction_id):
        self.delete_transaction_dialog = MDDialog(
            title="Confirm Delete",
            text="Are you sure you want to delete this transaction?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: close_delete_transaction_dialog(dialog_screen=self.delete_transaction_dialog)
                ),
                MDFlatButton(
                    text="DELETE",
                    on_release=lambda x: perform_delete_transaction(self, transaction_id, dialog_screen=self.delete_transaction_dialog)
                )
            ]
        )
        self.delete_transaction_dialog.open()

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
                    "text": account[1],
                    "on_release": lambda x=account: self.select_account(x[0], x[1])
                }
            )

        self.account_menu = MDDropdownMenu(
            caller=self.ids.account_selector,
            items=menu_items,
        )

        self.account_menu.open()

    def select_account(self, account_id, account_name):
        self.ids.account_label.text = account_name
        self.selected_account_id = account_id
        self.account_menu.dismiss()
        self.load_dashboard()

    def toggle_balance(self):
        self.balance_visible = not self.balance_visible
        self.load_summary()