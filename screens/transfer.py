from kivy.factory import Factory
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from database.account_repository import get_all_accounts
from services.transfer_services import (
    get_transfer_for_edit,
    save_transfer as save_transfer_workflow,
)
from utils.amount_input import apply_amount_key
from utils.transaction_datetime import (
    format_date_label,
    format_time_label,
    get_current_transaction_datetime_labels,
    parse_date_label,
    parse_time_label,
)
from widgets.date_time_pickers import DatePickerDialog, TimePickerDialog
from widgets.input_dialog import InputDialog
from widgets.overlays import EnkryonSelectionPanel

from .action_results import render_action_result
from .transfer_form_state import TransferFormState


class TransferScreen(Screen):

    ACCOUNT_ROLES = {"source", "destination"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.KEYS = [
            "1", "2", "3", "backspace",
            "4", "5", "6", "C",
            "7", "8", "9", ".",
            "", "0", "00", "",
        ]

        self.form_state = TransferFormState()
        self.preserve_form_on_next_enter = False
        self.account_creation_role = None
        self.build_keypad()


    def go_to_dashboard(self):
        self.reset_form()
        self.manager.current = "dashboard"


    def press_key(self, key):
        self.form_state.amount = apply_amount_key(
            self.form_state.amount,
            key,
        )
        self.update_amount_label()


    def update_amount_label(self):
        self.ids.amount_label.text = f"₱ {self.form_state.amount}"


    def on_pre_enter(self):
        if getattr(self, "preserve_form_on_next_enter", False):
            self.preserve_form_on_next_enter = False
            self.reconcile_preserved_accounts()
            self.render_form_state()
            return

        if self.form_state.transfer_id is not None:
            return

        self.reset_form()


    def reconcile_preserved_accounts(self):
        accounts_by_id = {
            account.account_id: account
            for account in get_all_accounts()
        }
        state = self.form_state

        source_account = accounts_by_id.get(state.source_account_id)
        if state.source_account_id is not None:
            if source_account is None:
                state.clear_source_account_selection()
            else:
                state.source_account_name = source_account.name

        destination_account = accounts_by_id.get(
            state.destination_account_id
        )
        if state.destination_account_id is not None:
            if destination_account is None:
                state.clear_destination_account_selection()
            else:
                state.destination_account_name = destination_account.name

        if (
            state.source_account_id is not None
            and state.source_account_id == state.destination_account_id
        ):
            state.clear_destination_account_selection()


    def build_keypad(self):
        self.ids.keypad_container.clear_widgets()

        for key in self.KEYS:
            button = Factory.KeypadButton()

            if key == "backspace":
                button.ids.label.opacity = 0
                button.ids.icon.opacity = 1
                button.ids.icon.icon = "backspace"
            elif key == "":
                self.ids.keypad_container.add_widget(Widget())
                continue
            else:
                button.ids.icon.opacity = 0
                button.ids.label.opacity = 1
                button.ids.label.text = key

            button.bind(
                on_release=lambda _, value=key: self.press_key(value)
            )
            self.ids.keypad_container.add_widget(button)


    def clear(self):
        self.form_state.amount = "0"
        self.update_amount_label()


    def reset_form(self):
        date_label, time_label = get_current_transaction_datetime_labels()
        self.form_state = TransferFormState.empty(
            date_label,
            time_label,
        )
        self.account_creation_role = None
        self.render_form_state()


    def render_form_state(self):
        state = self.form_state

        self.ids.source_account_label.text = state.source_account_name
        self.ids.destination_account_label.text = (
            state.destination_account_name
        )
        self.ids.date_label.text = state.date_label
        self.ids.time_label.text = state.time_label

        self.update_amount_label()
        self.set_notes(state.notes)


    def open_source_account_menu(self):
        self.open_account_menu("source")


    def open_destination_account_menu(self):
        self.open_account_menu("destination")


    def open_account_menu(self, role):
        if role not in self.ACCOUNT_ROLES:
            raise ValueError(f"Unknown transfer account role: {role}")

        accounts = get_all_accounts()
        state = self.form_state

        label = (
            self.ids.source_account_label
            if role == "source"
            else self.ids.destination_account_label
        )
        if not accounts:
            label.text = "No Accounts"

        select_account = (
            self.select_source_account
            if role == "source"
            else self.select_destination_account
        )
        selected_text = (
            state.source_account_name
            if role == "source"
            else state.destination_account_name
        )

        menu_items = [
            {
                "text": account.name,
                "on_release": (
                    lambda x=account, callback=select_account:
                    callback(x.account_id, x.name)
                ),
            }
            for account in accounts
        ]
        menu_items.append(
            {
                "text": "Add New Account",
                "is_navigation": True,
                "on_release": (
                    lambda selected_role=role:
                    self.open_add_account_screen(selected_role)
                ),
            }
        )

        menu = EnkryonSelectionPanel(
            title=(
                "Select Source Account"
                if role == "source"
                else "Select Destination Account"
            ),
            selected_text=selected_text,
            options=menu_items,
        )
        setattr(self, f"{role}_account_menu", menu)
        menu.open()


    def select_source_account(self, account_id, account_name):
        self.form_state.select_source_account(account_id, account_name)
        if self.form_state.destination_account_id == account_id:
            self.form_state.clear_destination_account_selection()
        self.render_form_state()
        self.source_account_menu.dismiss()


    def select_destination_account(self, account_id, account_name):
        self.form_state.select_destination_account(
            account_id,
            account_name,
        )
        if self.form_state.source_account_id == account_id:
            self.form_state.clear_source_account_selection()
        self.render_form_state()
        self.destination_account_menu.dismiss()


    def open_add_account_screen(self, role):
        if role not in self.ACCOUNT_ROLES:
            raise ValueError(f"Unknown transfer account role: {role}")

        self.preserve_form_on_next_enter = True
        self.account_creation_role = role

        accounts_screen = self.manager.get_screen("accounts")
        accounts_screen.return_screen = "transfer"
        accounts_screen.account_created_callback = (
            self.select_created_account
        )

        menu = getattr(self, f"{role}_account_menu", None)
        if menu is not None:
            menu.dismiss()

        self.manager.current = "accounts"


    def select_created_account(self, account_name):
        normalized_name = account_name.strip().casefold()
        account = next(
            (
                account
                for account in get_all_accounts()
                if account.name.strip().casefold() == normalized_name
            ),
            None,
        )

        if account is None:
            return

        if self.account_creation_role == "destination":
            self.form_state.select_destination_account(
                account.account_id,
                account.name,
            )
        else:
            self.form_state.select_source_account(
                account.account_id,
                account.name,
            )

        self.account_creation_role = None
        self.render_form_state()


    def set_current_date_time(self):
        date_label, time_label = get_current_transaction_datetime_labels()
        self.form_state.date_label = date_label
        self.form_state.time_label = time_label
        self.ids.date_label.text = date_label
        self.ids.time_label.text = time_label


    def open_date_picker(self):
        selected_date = parse_date_label(self.form_state.date_label)
        DatePickerDialog(
            callback=self.set_date,
            initial_date=selected_date,
        ).open()


    def open_time_picker(self):
        current_time = parse_time_label(self.form_state.time_label)
        TimePickerDialog(
            callback=self.set_time,
            initial_time=current_time,
        ).open()


    def set_date(self, selected_date):
        self.form_state.date_label = format_date_label(selected_date)
        self.ids.date_label.text = self.form_state.date_label


    def set_time(self, selected_time):
        self.form_state.time_label = format_time_label(selected_time)
        self.ids.time_label.text = self.form_state.time_label


    def save_transfer(self):
        result = save_transfer_workflow(
            **self.form_state.to_save_arguments()
        )
        render_action_result(result)

        if not result.success:
            return

        self.form_state.transfer_id = None

        dashboard = self.manager.get_screen("dashboard")
        dashboard.load_dashboard()
        self.manager.current = "dashboard"


    def load_transfer(self, transfer_id):
        transfer = get_transfer_for_edit(transfer_id)
        self.form_state = TransferFormState.from_transfer(transfer)
        self.render_form_state()


    def add_notes(self):
        InputDialog(
            title="Notes",
            hint_text="Enter notes...",
            text=self.form_state.notes,
            callback=self.set_notes,
        ).open()


    def set_notes(self, notes):
        self.form_state.set_notes(notes)

        if self.form_state.notes:
            self.ids.notes_label.text = self.form_state.notes
            self.ids.notes_label.theme_text_color = "Primary"
        else:
            self.ids.notes_label.text = "Add notes"
            self.ids.notes_label.theme_text_color = "Custom"
