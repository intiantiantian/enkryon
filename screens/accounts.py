from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton

from widgets.account_card import AccountCard

from database.account_repository import get_all_accounts, insert_account, update_account, delete_account

class AccountsScreen(Screen):

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'

    def go_to_add_transaction(self):
        self.manager.current = 'add_transaction'

    def on_pre_enter(self):
        self.rename_dialog = None
        self.load_accounts()

    def load_accounts(self):
        self.ids.accounts_container.clear_widgets()

        for account in get_all_accounts():
            card = AccountCard()
            card.screen = self
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

    def open_rename_dialog(self, account_id, account_name):

        if self.rename_dialog:
            self.rename_dialog.dismiss()
        
        self.rename_dialog = MDDialog(
            title="Rename Account",
            type="custom",
            content_cls=MDTextField(
                text=account_name,
                multiline=False
            ),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=self.close_rename_dialog
                ),
                MDFlatButton(
                    text="RENAME",
                    on_release=lambda x: self.rename_account(account_id)
                )
            ]
        )
        self.rename_dialog.open()

    def close_rename_dialog(self, *args):
        self.rename_dialog.dismiss()
        self.rename_dialog = None

    def rename_account(self, account_id):

        new_name = self.rename_dialog.content_cls.text.strip()
        if not new_name:
            print("New account name cannot be empty.")
            return
        
        success = update_account(account_id, new_name)

        if success:
            print(f"Account renamed to '{new_name}' successfully.")
            self.close_rename_dialog()
            self.load_accounts()
        else:
            print(f"Account name '{new_name}' already exists.")

    def perform_delete_account(self, account_id):
        self.close_delete_dialog()
        delete_account(account_id)
        print(f"Account with ID '{account_id}' deleted successfully.")
        self.load_accounts()

    def confirm_delete_account(self, account_id):
        self.delete_dialog = MDDialog(
            title="Confirm Delete",
            text="Are you sure you want to delete this account?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=self.close_delete_dialog
                ),
                MDFlatButton(
                    text="DELETE",
                    on_release=lambda x: self.perform_delete_account(account_id)
                )
            ]
        )
        self.delete_dialog.open()

    def close_delete_dialog(self, *args):
        self.delete_dialog.dismiss()