from services.transaction_services import (
    delete_transaction_by_id,
    restore_deleted_transaction,
)

from widgets.overlays import EnkryonConfirmationDialog

from .action_results import render_action_result

class TransactionListActionsMixin:

    def set_transaction_filter(self, transaction_type):
        filter_state = getattr(self, "filter_state", None)
        if filter_state is None:
            self.transaction_filter = transaction_type
        else:
            filter_state.select_transaction_type(
                transaction_type
            )

        self.ids.all_filter.set_selected(transaction_type is None)
        self.ids.income_filter.set_selected(
            transaction_type == "income"
        )
        self.ids.expense_filter.set_selected(
            transaction_type == "expense"
        )

        self.refresh_transaction_list()


    def get_empty_transaction_action(self):
        filter_state = getattr(self, "filter_state", None)
        if filter_state is None:
            filters_active = (
                self.transaction_filter is not None
                or getattr(
                    self,
                    "selected_account_id",
                    None,
                ) is not None
            )
        else:
            filters_active = filter_state.is_active

        if filters_active:
            return "SHOW ALL", self.show_all_transactions

        return "ADD TRANSACTION", self.go_to_add_transaction


    def show_all_transactions(self):
        self.set_transaction_filter(None)


    def edit_transaction(self, transaction_id):
        screen = self.manager.get_screen("add_transaction")
        screen.load_transaction(transaction_id)
        self.manager.current = "add_transaction"


    def delete_transaction(self, transaction_id):
        result = delete_transaction_by_id(transaction_id)
        self.close_delete_transaction_dialog()

        snackbar_options = None
        if result.success:
            snackbar_options = {
                "action_text": "UNDO",
                "action_callback": lambda:
                    self.undo_transaction_delete(
                        result.deleted_transaction
                    ),
                "duration": 8,
            }

        render_action_result(
            result,
            refresh=self.refresh_after_transaction_delete,
            refresh_required=result.success,
            snackbar_options=snackbar_options,
        )


    def undo_transaction_delete(self, transaction):
        result = restore_deleted_transaction(transaction)
        render_action_result(
            result,
            refresh=self.refresh_after_transaction_delete,
            refresh_required=result.success,
        )


    def confirm_delete_transaction(self, transaction_id):
        self.delete_transaction_dialog = (
            EnkryonConfirmationDialog(
                title="Delete Transaction?",
                message=(
                    "This transaction will be permanently "
                    "deleted."
                ),
                confirm_callback=lambda:
                    self.delete_transaction(transaction_id),
                cancel_callback=(
                    self.close_delete_transaction_dialog
                ),
            )
        )
        self.delete_transaction_dialog.open()


    def close_delete_transaction_dialog(self, *args):
        if self.delete_transaction_dialog:
            self.delete_transaction_dialog.dismiss()
            self.delete_transaction_dialog = None


    def refresh_after_transaction_delete(self):
        self.refresh_transaction_list()
