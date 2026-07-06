from kivy.uix.screenmanager import Screen

from widgets.account_card import AccountCard

from database.account_repository import get_all_accounts, insert_account

class AccountsScreen(Screen):

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'

    def go_to_add_transaction(self):
        self.manager.current = 'add_transaction'

    def on_pre_enter(self):
        self.load_accounts()

    def load_accounts(self):
        self.ids.accounts_container.clear_widgets()

        for account in get_all_accounts():
            card = AccountCard()
            card.set_account(account)
            self.ids.accounts_container.add_widget(card)

    def add_account(self):
        account_name = self.ids.account_name_input.text.strip()
        if not account_name:
            print("Account name cannot be empty.")
            return
        
        success = insert_account(account_name)

        if success:
            print(f"Account '{account_name}' added successfully.")
            self.ids.account_name_input.text = ''
            self.load_accounts()
        else:
            print(f"Account '{account_name}' already exists.")
