from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu

from database.account_repository import get_all_accounts
from database.transaction_repository import (
    delete_transaction,
    get_transactions,
    get_total_income,
    get_total_expense,
    get_current_balance,
)

from widgets.transaction_card import TransactionCard

class DashboardScreen(Screen):

    selected_account_id = None
    balance_visible = True

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
        if self.selected_account_id is None:
            self.ids.account_button.text = "All Accounts"

        self.load_dashboard()

    def load_dashboard(self):
        balance = get_current_balance(self.selected_account_id)
        income = get_total_income(self.selected_account_id)
        expense = get_total_expense(self.selected_account_id)

        if self.balance_visible:
            self.ids.balance_label.text = f"₱ {balance:,.2f}"
            self.ids.income_label.text = f"₱ {income:,.2f}"
            self.ids.expense_label.text = f"₱ {expense:,.2f}"
            self.ids.eye_button.icon = "eye"
        else:
            self.ids.balance_label.text = "₱ ******"
            self.ids.income_label.text = "₱ ******"
            self.ids.expense_label.text = "₱ ******"
            self.ids.eye_button.icon = "eye-off"

        self.load_recent_transactions()

    def load_recent_transactions(self):
        self.ids.transactions_container.clear_widgets()

        transactions = get_transactions(limit=5, account_id=self.selected_account_id)

        for transaction in transactions:
            card = TransactionCard()
            card.screen = self
            card.set_transaction(transaction)
            self.ids.transactions_container.add_widget(card)

    def edit_transaction(self, transaction_id):
        screen = self.manager.get_screen('add_transaction')
        screen.load_transaction(transaction_id)
        self.manager.current = 'add_transaction'

    def perform_delete_transaction(self, transaction_id):
        self.close_delete_transaction_dialog()
        delete_transaction(transaction_id)
        print(f"Transaction with ID '{transaction_id}' deleted successfully.")
        self.load_dashboard()

    def confirm_delete_transaction(self, transaction_id):
        self.delete_transaction_dialog = MDDialog(
            title="Confirm Delete",
            text="Are you sure you want to delete this transaction?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=self.close_delete_transaction_dialog
                ),
                MDFlatButton(
                    text="DELETE",
                    on_release=lambda x: self.perform_delete_transaction(transaction_id)
                )
            ]
        )
        self.delete_transaction_dialog.open()

    def close_delete_transaction_dialog(self, *args):
        self.delete_transaction_dialog.dismiss()

    def open_account_menu(self):
        accounts = get_all_accounts()
        if not accounts:
            self.ids.account_button.text = 'No Accounts'
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
            caller=self.ids.account_button,
            items=menu_items,
        )

        self.account_menu.open()

    def select_account(self, account_id, account_name):
        self.ids.account_button.text = account_name
        self.selected_account_id = account_id
        self.account_menu.dismiss()
        self.load_dashboard()

    def toggle_balance(self):
        self.balance_visible = not self.balance_visible
        self.load_dashboard()