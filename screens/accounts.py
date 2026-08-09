from kivy.uix.screenmanager import Screen

from .action_results import render_action_result

from services.account_services import (
    create_account as create_account_workflow,
    get_accounts_for_view,
    remove_account as remove_account_workflow,
    rename_account as rename_account_workflow,
)
from services.interest_services import save_interest_profile

from .account_interest_state import (
    load_account_interest_view,
    parse_apr_micros,
    parse_effective_date,
)

from widgets.account_card import AccountCard
from widgets.input_dialog import InputDialog
from widgets.empty_state import EmptyState
from widgets.overlays import EnkryonConfirmationDialog
from widgets.interest_dialog import InterestSettingsDialog


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
            interest_state = load_account_interest_view(account.account_id)
            card.set_interest_summary(interest_state.summary_text)
            self.ids.accounts_container.add_widget(card)


    def open_interest_dialog(self, account_id, account_name):
        state = load_account_interest_view(account_id)
        self.interest_dialog = InterestSettingsDialog(
            account_name=account_name,
            apr_text=state.apr_text,
            effective_date_text=state.effective_date_text,
            day_count_text=state.day_count_text,
            today_estimate_text=state.today_estimate_text,
            accumulated_estimate_text=state.accumulated_estimate_text,
            is_enabled=state.enabled,
            save_callback=lambda apr, effective_date: self.save_interest_settings(
                account_id, apr, effective_date
            ),
            disable_callback=lambda effective_date: self.disable_interest_settings(
                account_id, effective_date
            ),
        )
        self.interest_dialog.open()


    def save_interest_settings(self, account_id, apr_text, effective_date_text):
        try:
            annual_rate_micros = parse_apr_micros(apr_text)
            effective_date = parse_effective_date(effective_date_text)
        except ValueError as error:
            from utils.snackbar import show_snackbar
            show_snackbar(str(error))
            return False

        result = save_interest_profile(
            account_id,
            annual_rate_micros,
            effective_date,
            enabled=True,
        )
        render_action_result(
            result,
            refresh=self.load_accounts,
            refresh_required=result.success,
        )
        return result.success


    def disable_interest_settings(self, account_id, effective_date_text):
        try:
            effective_date = parse_effective_date(effective_date_text)
        except ValueError as error:
            from utils.snackbar import show_snackbar
            show_snackbar(str(error))
            return False

        result = save_interest_profile(
            account_id,
            0,
            effective_date,
            enabled=False,
        )
        render_action_result(
            result,
            refresh=self.load_accounts,
            refresh_required=result.success,
        )
        return result.success


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
