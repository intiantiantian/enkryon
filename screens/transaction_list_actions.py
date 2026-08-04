from services.transaction_services import (
    delete_transaction_by_id,
    restore_deleted_transaction,
)
from services.transfer_services import (
    delete_transfer_by_id,
    restore_deleted_transfer,
)

from widgets.overlays import EnkryonConfirmationDialog

from .action_results import render_action_result

class TransactionListActionsMixin:

    def set_transaction_filter(self, transaction_type):
        self.filter_state.select_transaction_type(
            transaction_type
        )

        self.ids.all_filter.set_selected(
            transaction_type is None
        )
        self.ids.income_filter.set_selected(
            transaction_type == "income"
        )
        self.ids.expense_filter.set_selected(
            transaction_type == "expense"
        )
        transfer_filter = getattr(
            self.ids,
            "transfer_filter",
            None,
        )
        if transfer_filter is not None:
            transfer_filter.set_selected(
                transaction_type == "transfer"
            )

        self.refresh_transaction_list()


    def get_empty_transaction_action(self):
        if self.filter_state.is_active:
            return "SHOW ALL", self.show_all_transactions

        return "ADD TRANSACTION", self.go_to_add_transaction


    def show_all_transactions(self):
        self.set_transaction_filter(None)


    def edit_transaction(self, transaction_id):
        screen = self.manager.get_screen("add_transaction")
        screen.load_transaction(transaction_id)
        self.manager.current = "add_transaction"


    def edit_transfer(self, transfer_id):
        screen = self.manager.get_screen("transfer")
        screen.load_transfer(transfer_id)
        self.manager.current = "transfer"


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


    def delete_transfer(self, transfer_id):
        result = delete_transfer_by_id(transfer_id)
        self.close_delete_transaction_dialog()

        snackbar_options = None
        if result.success:
            snackbar_options = {
                "action_text": "UNDO",
                "action_callback": lambda:
                    self.undo_transfer_delete(
                        result.deleted_transfer
                    ),
                "duration": 8,
            }

        render_action_result(
            result,
            refresh=self.refresh_after_transaction_delete,
            refresh_required=result.success,
            snackbar_options=snackbar_options,
        )


    def undo_transfer_delete(self, transfer):
        result = restore_deleted_transfer(transfer)
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


    def confirm_delete_transfer(self, transfer_id):
        self.delete_transaction_dialog = (
            EnkryonConfirmationDialog(
                title="Delete Transfer?",
                message=(
                    "This transfer will be permanently deleted."
                ),
                confirm_callback=lambda:
                    self.delete_transfer(transfer_id),
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
