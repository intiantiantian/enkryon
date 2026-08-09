from datetime import date

from kivy.uix.screenmanager import Screen

from .action_results import render_action_result

from services.account_services import (
    create_account as create_account_workflow,
    get_accounts_for_view,
    remove_account as remove_account_workflow,
    rename_account as rename_account_workflow,
)
from services.interest_services import (
    get_interest_reconciliation_preview,
    reconcile_interest_credit,
    save_interest_profile,
)

from .account_interest_state import (
    load_account_interest_view,
    parse_apr_micros,
    parse_effective_date,
)

from widgets.account_card import AccountCard
from widgets.input_dialog import InputDialog
from widgets.empty_state import EmptyState
from widgets.overlays import (
    EnkryonConfirmationDialog,
    EnkryonSelectionPanel,
)
from widgets.interest_dialog import (
    InterestReconciliationDialog,
    InterestSettingsDialog,
)
from database.category_repository import get_categories_by_type
from utils.money import format_money, pesos_to_centavos


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
            reconcile_callback=lambda: self.open_interest_reconciliation(
                account_id, account_name
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


    def open_interest_reconciliation(self, account_id, account_name):
        credit_date = date.today().isoformat()
        preview = get_interest_reconciliation_preview(
            account_id,
            credit_date,
        )
        count_text = (
            f"{preview.accrual_count} estimated day"
            if preview.accrual_count == 1
            else f"{preview.accrual_count} estimated days"
        )
        self.reconciliation_dialog = InterestReconciliationDialog(
            account_name=account_name,
            estimated_text=format_money(preview.estimated_centavos),
            accrual_count_text=count_text,
            credit_date_text=credit_date,
            save_callback=lambda amount, credit, category: self.reconcile_interest_credit(
                account_id, amount, credit, category
            ),
            category_callback=self.open_interest_category_menu,
            preview_callback=lambda credit: self.refresh_interest_reconciliation_preview(
                account_id, credit
            ),
        )
        self.reconciliation_dialog.open()


    def refresh_interest_reconciliation_preview(self, account_id, credit_date_text):
        text = (credit_date_text or "").strip()
        try:
            parsed = date.fromisoformat(text)
        except ValueError:
            return None
        if parsed.isoformat() != text:
            return None

        try:
            preview = get_interest_reconciliation_preview(account_id, text)
        except ValueError:
            return None
        return (
            preview.accrual_count,
            format_money(preview.estimated_centavos),
        )


    def open_interest_category_menu(self, dialog):
        categories = get_categories_by_type("income")
        if not categories:
            from utils.snackbar import show_snackbar
            show_snackbar(
                "Create an Income category before reconciling interest."
            )
            return

        options = [
            {
                "text": f"{category.group_name} · {category.name}",
                "selected": category.category_id == dialog.category_id,
                "on_release": lambda item=category: self.select_interest_category(
                    dialog, item
                ),
            }
            for category in categories
        ]
        self.interest_category_menu = EnkryonSelectionPanel(
            title="Select Income Category",
            selected_text=dialog.category_name,
            options=options,
        )
        self.interest_category_menu.open()


    def select_interest_category(self, dialog, category):
        dialog.set_category(category.category_id, category.name)
        if getattr(self, "interest_category_menu", None):
            self.interest_category_menu.dismiss()
            self.interest_category_menu = None


    def reconcile_interest_credit(
        self,
        account_id,
        actual_amount_text,
        credit_date_text,
        category_id,
    ):
        try:
            actual_amount_centavos = pesos_to_centavos(
                (actual_amount_text or "").strip()
            )
        except (ValueError, OverflowError) as error:
            from utils.snackbar import show_snackbar
            show_snackbar(str(error))
            return False

        text = (credit_date_text or "").strip()
        try:
            parsed_date = date.fromisoformat(text)
        except ValueError:
            from utils.snackbar import show_snackbar
            show_snackbar("Credit date must use YYYY-MM-DD.")
            return False
        if parsed_date.isoformat() != text:
            from utils.snackbar import show_snackbar
            show_snackbar("Credit date must use YYYY-MM-DD.")
            return False

        result = reconcile_interest_credit(
            account_id=account_id,
            actual_amount_centavos=actual_amount_centavos,
            credit_date=text,
            category_id=category_id,
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
