from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from services.transaction_services import (
    delete_transaction_by_id,
    restore_deleted_transaction,
)

from .action_results import render_action_result

class TransactionListActionsMixin:

    def set_transaction_filter(self, transaction_type):
        self.transaction_filter = transaction_type

        self.ids.all_filter.set_selected(transaction_type is None)
        self.ids.income_filter.set_selected(
            transaction_type == "income"
        )
        self.ids.expense_filter.set_selected(
            transaction_type == "expense"
        )

        self.refresh_transaction_list()


    def edit_transaction(self, transaction_id):
        screen = self.manager.get_screen("add_transaction")
        screen.load_transaction(transaction_id)
        self.manager.current = "add_transaction"


    def delete_transaction(self, transaction_id):
        result = delete_transaction_by_id(transaction_id)
        self.delete_transaction_dialog.dismiss()

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
        self.delete_transaction_dialog = MDDialog(
            title="Confirm Delete",
            text=(
                "Delete this transaction? "
                "You can undo this action for a few seconds."
            ),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x:
                        self.delete_transaction_dialog.dismiss()
                ),
                MDFlatButton(
                    text="DELETE",
                    on_release=lambda x:
                        self.delete_transaction(transaction_id)
                )
            ]
        )
        self.delete_transaction_dialog.open()


    def refresh_after_transaction_delete(self):
        self.refresh_transaction_list()
