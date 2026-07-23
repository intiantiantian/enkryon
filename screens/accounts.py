from kivy.uix.screenmanager import Screen

from .action_results import render_action_result

from services.account_services import (
    create_account as create_account_workflow,
    get_accounts_for_view,
    remove_account as remove_account_workflow,
    rename_account as rename_account_workflow,
)

from widgets.account_card import AccountCard
from widgets.input_dialog import InputDialog
from widgets.empty_state import EmptyState
from widgets.overlays import EnkryonConfirmationDialog


class AccountsScreen(Screen):

    return_screen = "dashboard"
    account_created_callback = None


    def go_back(self):
        destination = self.return_screen
        self.return_screen = "dashboard"
        self.account_created_callback = None
        self.manager.current = destination


    def go_to_add_transaction(self):
        self.manager.current = 'add_transaction'


    def on_pre_enter(self):
        self.load_accounts()
        self.delete_dialog = None


    def load_accounts(self):
        self.ids.accounts_container.clear_widgets()

        accounts = get_accounts_for_view()

        if not accounts:
            self.ids.accounts_container.add_widget(
                EmptyState(
                    icon="wallet-outline",
                    title="No accounts yet",
                    message=(
                        "Create an account to start tracking your money."
                    ),
                    action_text="ADD ACCOUNT",
                    action_callback=self.add_account,
                )
            )
            return

        for account in accounts:
            card = AccountCard()
            card.screen = self
            card.set_account(account)
            self.ids.accounts_container.add_widget(card)


    def add_account(self):
        InputDialog(
            title="New Account",
            hint_text="Account name...",
            callback=self.save_account
        ).open()


    def save_account(self, account_name):
        result = create_account_workflow(account_name)
        render_action_result(
            result,
            refresh=self.load_accounts,
            refresh_required=result.success,
        )
        callback = getattr(self, "account_created_callback", None)
        if result.success and callback is not None:
            callback((account_name or "").strip())


    def open_rename_dialog(self, account_id, account_name):
        InputDialog(
            title="Rename Account",
            hint_text="Account name...",
            text=account_name,
            callback=lambda new_name: self.rename_account(
                account_id,
                new_name,
            ),
        ).open()


    def rename_account(self, account_id, new_name):
        result = rename_account_workflow(account_id, new_name)
        render_action_result(
            result,
            refresh=self.load_accounts,
            refresh_required=result.success,
        )


    def perform_delete_account(self, account_id):
        self.close_delete_dialog()

        result = remove_account_workflow(account_id)
        render_action_result(
            result,
            refresh=self.load_accounts,
            refresh_required=result.success,
        )


    def confirm_delete_account(self, account_id):
        self.delete_dialog = EnkryonConfirmationDialog(
            title="Delete Account?",
            message=(
                "Accounts with existing transactions cannot "
                "be deleted. Delete this account?"
            ),
            confirm_callback=lambda:
                self.perform_delete_account(account_id),
            cancel_callback=self.close_delete_dialog,
        )
        self.delete_dialog.open()


    def close_delete_dialog(self, *args):
        if self.delete_dialog:
            self.delete_dialog.dismiss()
            self.delete_dialog = None
