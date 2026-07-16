from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.widget import Widget
from kivy.factory import Factory

from database.account_repository import get_all_accounts
from database.category_group_repository import get_category_groups_by_type
from database.category_repository import get_categories_by_group
from database.transaction_repository import (
    insert_transaction,
    get_transaction_by_id,
    update_transaction
    )

from utils.amount_input import apply_amount_key
from utils.money import centavos_to_peso_text
from utils.snackbar import show_snackbar
from utils.transaction_validation import validate_transaction_form
from utils.transaction_payload import build_transaction_payload
from utils.transaction_datetime import (
    format_date_label,
    format_time_label,
    get_current_transaction_datetime_labels,
    parse_date_label,
    parse_time_label,
    split_database_datetime,
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

        self.amount = '0'
        self.transaction_type = None
        self.build_keypad()

    def go_to_dashboard(self):
        self.reset_form()
        self.manager.current = 'dashboard'
    
    def press_key(self, key):
        self.amount = apply_amount_key(self.amount, key)
        self.update_amount_label()

    def update_amount_label(self):
        self.ids.amount_label.text = f'₱ {self.amount}'
    
    def on_pre_enter(self):

        if getattr(self, 'editing_transaction_id', None):
            return
        
        self.transaction_type = None
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
        self.amount = '0'
        self.update_amount_label()

    def reset_form(self):
        self.ids.income_button.set_selected(False)
        self.ids.expense_button.set_selected(False)
    
        self.selected_account_id = None
        self.ids.account_selector.text = 'Select Account'

        self.selected_group_id = None
        self.ids.group_label.text = 'No Transaction Type Selected'
        self.ids.group_selector.disabled = True

        self.selected_category_id = None
        self.ids.category_label.text = 'No Category Group Selected'
        self.ids.category_selector.disabled = True

        self.set_current_date_time()
        self.clear()

        self.set_notes('')

    def open_account_menu(self):
        accounts = get_all_accounts()
        if not accounts:
            self.ids.account_selector.text = 'No Accounts'
            return

        menu_items = []

        for account in accounts:
            menu_items.append(
                {
                    "text": account[1],
                    "on_release": lambda x=account: self.select_account(x[0], x[1])
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
        self.ids.account_selector.text = account_name
        self.selected_account_id = account_id
        self.account_menu.dismiss()

    def open_add_account_screen(self):
        self.manager.current = 'accounts'
        self.account_menu.dismiss()

    def update_groups_button(self, transaction_type):
        self.transaction_type = transaction_type
        self.selected_group_id = None
        self.selected_category_id = None

        self.ids.income_button.set_selected(transaction_type == 'income')
        self.ids.expense_button.set_selected(transaction_type == 'expense')

        self.ids.group_selector.disabled = False
        self.ids.group_label.text = 'Select Category Group'

        self.ids.category_selector.disabled = True
        self.ids.category_label.text = 'No Category Group Selected'

    def update_categories_button(self):
        self.ids.category_selector.disabled = False
        self.ids.category_label.text = 'Select Category'
        self.selected_category_id = None

    def open_groups_menu(self):
        groups = get_category_groups_by_type(self.transaction_type)
        if not groups:
            self.ids.group_label.text = 'No Category Groups Created'
            return

        menu_items = []

        for group in groups:
            menu_items.append(
                {
                    "text": group[1],
                    "on_release": lambda x=group: self.select_group(x[0], x[1])
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
        self.update_categories_button()

        self.ids.group_label.text = group_name
        self.selected_group_id = group_id
        self.groups_menu.dismiss()

    def open_categories_menu(self):
        categories = get_categories_by_group(self.selected_group_id)
        if not categories:
            self.ids.category_label.text = 'No Category Created'
            return
        
        menu_items = []

        for category in categories:
            menu_items.append(
                {
                    "text": category[2],
                    "on_release": lambda x=category: self.select_category(x[0], x[2])
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
        self.ids.category_label.text = category_name
        self.selected_category_id = category_id
        self.categories_menu.dismiss()

    def open_manage_category_screen(self):
        self.manager.current = 'categories'
        if hasattr(self, "groups_menu"):
            self.groups_menu.dismiss()
        if hasattr(self, "categories_menu"):
            self.categories_menu.dismiss()

    def set_current_date_time(self):
        date_label, time_label = get_current_transaction_datetime_labels()
        self.ids.date_label.text = date_label
        self.ids.time_label.text = time_label

    def open_date_picker(self):
        selected_date = parse_date_label(self.ids.date_label.text)
        DatePickerDialog(callback=self.set_date, initial_date=selected_date).open()

    def open_time_picker(self):
        current_time = parse_time_label(self.ids.time_label.text)
        TimePickerDialog(callback=self.set_time, initial_time=current_time).open()

    def set_date(self, selected_date):
        self.ids.date_label.text = format_date_label(selected_date)

    def set_time(self, selected_time):
        self.ids.time_label.text = format_time_label(selected_time)

    def save_transaction(self):
        if not self.validate_form():
            return
        
        payload = build_transaction_payload(
            account_id=self.selected_account_id,
            amount=self.amount,
            category_id=self.selected_category_id,
            date_label=self.ids.date_label.text,
            time_label=self.ids.time_label.text,
            notes_label=self.ids.notes_label.text,
        )

        if getattr(self, "editing_transaction_id", None):
            update_transaction(
                payload["account_id"],
                payload["amount_centavos"],
                payload["category_id"],
                payload["date_time"],
                payload["notes"],
                self.editing_transaction_id,
            )
            self.editing_transaction_id = None
            show_snackbar("Transaction updated successfully.")
        else:
            insert_transaction(
                payload["account_id"],
                payload["amount_centavos"],
                payload["category_id"],
                payload["date_time"],
                payload["notes"],
            )
            show_snackbar("Transaction added successfully.")
        
        dashboard = self.manager.get_screen('dashboard')
        dashboard.load_dashboard()
        self.manager.current = 'dashboard'

    def validate_form(self):
        is_valid, message = validate_transaction_form(
            account_id=self.selected_account_id,
            amount=self.amount,
            transaction_type=self.transaction_type,
            category_id=self.selected_category_id,
        )

        if not is_valid:
            show_snackbar(message)
            return False

        return True
    
    def load_transaction(self, transaction_id):
        self.reset_form()

        transaction = get_transaction_by_id(transaction_id)

        (
            transaction_id,
            account_id,
            amount_centavos,
            category_id,
            date_time,
            notes,
            account_name,
            category_name,
            group_id,
            group_name,
            transaction_type            
        ) = transaction

        self.editing_transaction_id = transaction_id
    
        self.set_transaction_type(transaction_type)

        self.selected_account_id = account_id
        self.selected_group_id = group_id
        self.selected_category_id = category_id

        self.ids.account_selector.text = account_name
        self.ids.group_label.text = group_name
        self.ids.category_label.text = category_name
        self.ids.category_selector.disabled = False

        self.amount = centavos_to_peso_text(amount_centavos)
        self.update_amount_label()

        self.set_notes(notes)

        date_label, time_label = split_database_datetime(date_time)

        self.ids.date_label.text = date_label
        self.ids.time_label.text = time_label

    def set_transaction_type(self, transaction_type):

        self.transaction_type = transaction_type

        self.ids.income_button.set_selected(transaction_type == 'income')
        self.ids.expense_button.set_selected(transaction_type == 'expense')

        self.update_groups_button(transaction_type)

    def add_notes(self):
        InputDialog(
            title = 'Notes',
            hint_text = 'Enter notes...',
            text = self.ids.notes_label.text
                if self.ids.notes_label.text != 'Add notes'
                else '',
            callback = self.set_notes
        ).open()

    def set_notes(self, notes):
        if notes.strip():
            self.ids.notes_label.text = notes
            self.ids.notes_label.theme_text_color = 'Primary'
        else:
            self.ids.notes_label.text = 'Add notes'
            self.ids.notes_label.theme_text_color = 'Hint'