from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.widget import Widget
from kivy.factory import Factory

from database.account_repository import get_all_accounts
from database.category_group_repository import get_category_groups_by_type
from database.category_repository import get_categories_by_group

from services.transaction_services import (
    get_transaction_for_edit,
    save_transaction as save_transaction_workflow,
)

from .transaction_form_state import TransactionFormState
from .action_results import render_action_result

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

class AddTransactionScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.KEYS = [
            "1", "2", "3", "backspace",
            "4", "5", "6", "C",
            "7", "8", "9", ".",
            "", "0", "00", "",
        ]

        self.form_state = TransactionFormState()
        self.preserve_form_on_next_enter = False
        self.build_keypad()


    def go_to_dashboard(self):
        self.reset_form()
        self.manager.current = 'dashboard'


    def press_key(self, key):
        self.form_state.amount = apply_amount_key(
            self.form_state.amount,
            key,
        )
        self.update_amount_label()


    def update_amount_label(self):
        self.ids.amount_label.text = f'₱ {self.form_state.amount}'


    def on_pre_enter(self):
        if getattr(self, "preserve_form_on_next_enter", False):
            self.preserve_form_on_next_enter = False
            return

        if self.form_state.transaction_id is not None:
            return

        self.reset_form()


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
        self.form_state.amount = '0'
        self.update_amount_label()


    def reset_form(self):
        date_label, time_label = get_current_transaction_datetime_labels()
        self.form_state = TransactionFormState.empty(
            date_label,
            time_label,
        )
        self.render_form_state()


    def render_form_state(self):
        state = self.form_state

        self.ids.income_button.set_selected(
            state.transaction_type == 'income'
        )
        self.ids.expense_button.set_selected(
            state.transaction_type == 'expense'
        )

        self.ids.account_label.text = state.account_name

        self.ids.group_label.text = state.group_name
        self.ids.group_selector.disabled = state.transaction_type is None

        self.ids.category_label.text = state.category_name
        self.ids.category_selector.disabled = state.group_id is None

        self.ids.date_label.text = state.date_label
        self.ids.time_label.text = state.time_label

        self.update_amount_label()
        self.set_notes(state.notes)


    def open_account_menu(self):
        accounts = get_all_accounts()
        if not accounts:
            self.form_state.account_name = 'No Accounts'
            self.ids.account_label.text = self.form_state.account_name

        menu_items = []

        for account in accounts:
            menu_items.append(
                {
                    "text": account.name,
                    "on_release": lambda x=account:
                        self.select_account(
                            x.account_id,
                            x.name,
                        )
                }
            )

        menu_items.append(
            {
                "text": "Add New Account",
                "on_release": lambda: self.open_add_account_screen()
            }
        )

        self.account_menu = MDDropdownMenu(
            caller=self.ids.account_selector,
            items=menu_items,
        )

        self.account_menu.open()


    def select_account(self, account_id, account_name):
        self.form_state.select_account(account_id, account_name)
        self.render_form_state()
        self.account_menu.dismiss()


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

        self.form_state.select_account(account.account_id, account.name)
        self.render_form_state()


    def open_add_account_screen(self):
        self.preserve_form_on_next_enter = True

        accounts_screen = self.manager.get_screen("accounts")
        accounts_screen.return_screen = "add_transaction"

        accounts_screen.account_created_callback = (
            self.select_created_account
        )

        self.account_menu.dismiss()
        self.manager.current = "accounts"


    def update_groups_button(self, transaction_type):
        self.form_state.select_transaction_type(transaction_type)
        self.render_form_state()


    def open_groups_menu(self):
        groups = get_category_groups_by_type(
            self.form_state.transaction_type
        )
        if not groups:
            self.form_state.group_name = 'No Category Groups Created'
            self.ids.group_label.text = self.form_state.group_name

        menu_items = []

        for group in groups:
            menu_items.append(
                {
                    "text": group.name,
                    "on_release": lambda x=group:
                        self.select_group(
                            x.group_id,
                            x.name,
                        )
                }
            )

        menu_items.append(
            {
                "text": "Manage Category Groups",
                "on_release": lambda: self.open_manage_category_screen()
            }
        )

        self.groups_menu = MDDropdownMenu(
            caller=self.ids.group_selector,
            items=menu_items,
        )

        self.groups_menu.open()


    def select_group(self, group_id, group_name):
        self.form_state.select_group(group_id, group_name)
        self.render_form_state()
        self.groups_menu.dismiss()


    def select_created_group(self, transaction_type, group_name):
        normalized_name = group_name.strip().casefold()
        group = next(
            (
                group
                for group in get_category_groups_by_type(
                    transaction_type
                )
                if group.name.strip().casefold() == normalized_name
            ),
            None,
        )

        if group is None:
            return

        self.form_state.select_transaction_type(transaction_type)
        self.form_state.select_group(group.group_id, group.name)
        self.render_form_state()


    def open_categories_menu(self):
        categories = get_categories_by_group(self.form_state.group_id)
        if not categories:
            self.form_state.category_name = 'No Category Created'
            self.ids.category_label.text = self.form_state.category_name
        
        menu_items = []

        for category in categories:
            menu_items.append(
                {
                    "text": category.name,
                    "on_release": lambda x=category:
                        self.select_category(
                            x.category_id,
                            x.name,
                        )
                }
            )

        menu_items.append(
            {
                "text": "Manage Categories",
                "on_release": lambda: self.open_manage_category_screen()
            }
        )

        self.categories_menu = MDDropdownMenu(
            caller=self.ids.category_selector,
            items=menu_items,
        )

        self.categories_menu.open()


    def select_category(self, category_id, category_name):
        self.form_state.select_category(category_id, category_name)
        self.render_form_state()
        self.categories_menu.dismiss()


    def select_created_category(self, group_id, category_name):
        normalized_name = category_name.strip().casefold()
        category = next(
            (
                category
                for category in get_categories_by_group(group_id)
                if category.name.strip().casefold() == normalized_name
            ),
            None,
        )

        if category is None:
            return

        self.form_state.select_transaction_type(
            category.transaction_type
        )
        self.form_state.select_group(
            category.group_id,
            category.group_name,
        )
        self.form_state.select_category(
            category.category_id,
            category.name,
        )
        self.render_form_state()


    def open_manage_category_screen(self):
        self.preserve_form_on_next_enter = True

        categories_screen = self.manager.get_screen("categories")
        categories_screen.return_screen = "add_transaction"

        categories_screen.group_created_callback = (
            self.select_created_group
        )
        categories_screen.category_created_callback = (
            self.select_created_category
        )
        categories_screen.initial_transaction_type = (
            self.form_state.transaction_type
        )
        categories_screen.initial_group_id = self.form_state.group_id

        if hasattr(self, "groups_menu"):
            self.groups_menu.dismiss()
        if hasattr(self, "categories_menu"):
            self.categories_menu.dismiss()

        self.manager.current = "categories"


    def set_current_date_time(self):
        date_label, time_label = get_current_transaction_datetime_labels()
        self.form_state.date_label = date_label
        self.form_state.time_label = time_label
        self.ids.date_label.text = self.form_state.date_label
        self.ids.time_label.text = self.form_state.time_label


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


    def save_transaction(self):
        result = save_transaction_workflow(
            **self.form_state.to_save_arguments()
        )

        render_action_result(result)

        if not result.success:
            return

        self.form_state.transaction_id = None

        dashboard = self.manager.get_screen('dashboard')
        dashboard.load_dashboard()
        self.manager.current = 'dashboard'


    def load_transaction(self, transaction_id):
        transaction = get_transaction_for_edit(transaction_id)
        self.form_state = TransactionFormState.from_transaction(
            transaction
        )
        self.render_form_state()


    def set_transaction_type(self, transaction_type):
        self.update_groups_button(transaction_type)


    def add_notes(self):
        InputDialog(
            title='Notes',
            hint_text='Enter notes...',
            text=self.form_state.notes,
            callback=self.set_notes,
        ).open()


    def set_notes(self, notes):
        self.form_state.set_notes(notes)

        if self.form_state.notes:
            self.ids.notes_label.text = self.form_state.notes
            self.ids.notes_label.theme_text_color = 'Primary'
        else:
            self.ids.notes_label.text = 'Add notes'
            self.ids.notes_label.theme_text_color = 'Custom'
