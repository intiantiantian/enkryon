from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.utils import get_color_from_hex

from services.transaction_services import close_delete_transaction_dialog, load_transactions, perform_delete_transaction

class TransactionsScreen(Screen):

    transaction_filter = None

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'

    def on_pre_enter(self):
        self.ids.all_filter.md_bg_color = get_color_from_hex('#D5F4BE')
        self.ids.income_filter.md_bg_color = get_color_from_hex("#FFFFFF")
        self.ids.expense_filter.md_bg_color = get_color_from_hex("#FFFFFF")
        self.transaction_filter = None

        load_transactions(self)

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
        
        load_transactions(self)

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
                    on_release=lambda x: close_delete_transaction_dialog(dialog_screen=self.delete_transaction_dialog)                ),
                MDFlatButton(
                    text="DELETE",
                    on_release=lambda x: perform_delete_transaction(self, transaction_id, dialog_screen=self.delete_transaction_dialog)
                )
            ]
        )
        self.delete_transaction_dialog.open()