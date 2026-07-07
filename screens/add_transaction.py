from kivy.uix.screenmanager import Screen
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.menu import MDDropdownMenu

from database.transaction_repository import insert_transaction
from datetime import datetime

from database.account_repository import get_all_accounts
from database.category_group_repository import get_category_groups_by_type
from database.category_repository import get_categories_by_group

class AddTransactionScreen(Screen):
    
    def go_to_dashboard(self):
        self.manager.current = 'dashboard'
    
    amount = '0'

    def press_number(self, number):
        if self.amount == '0':
            self.amount = str(number)
        else:
            self.amount += str(number)
        self.update_amount_label()

    def add_decimal(self):
        if '.' not in self.amount:
            self.amount += '.'
        self.update_amount_label()
    
    def delete_last(self):
        if len(self.amount) > 1:
            self.amount = self.amount[:-1]
        else:
            self.amount = '0'
        self.update_amount_label()
    
    def clear(self):
        self.amount = '0'
        self.update_amount_label()

    def update_amount_label(self):
        self.ids.amount_label.text = f'₱ {self.amount}'

    def get_transaction_type(self):
        if self.ids.income_button.state == 'down':
            return 'income'
        elif self.ids.expense_button.state == 'down':
            return 'expense'
        return None
    
    def on_pre_enter(self):
        self.ids.income_button.state = 'normal'
        self.ids.expense_button.state = 'normal'
    
        self.selected_account_id = None
        self.ids.account_button.text = 'Select Account'

        self.selected_group_id = None
        self.ids.groups_button.text = 'No Transaction Type Selected'
        self.ids.groups_button.disabled = True

        self.selected_category_id = None
        self.ids.categories_button.text = 'No Category Group Selected'
        self.ids.categories_button.disabled = True

        self.set_current_date_time()
        self.clear()

        self.ids.notes_input.text = ''
        self.ids.notes_input.hint_text = 'Add notes (optional)'

    def open_account_menu(self):
        accounts = get_all_accounts()
        if not accounts:
            self.ids.account_button.text = 'No Accounts'
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
            caller=self.ids.account_button,
            items=menu_items,
        )

        self.account_menu.open()

    def select_account(self, account_id, account_name):
        self.ids.account_button.text = account_name
        self.selected_account_id = account_id
        self.account_menu.dismiss()

    def open_add_account_screen(self):
        self.manager.current = 'accounts'
        self.account_menu.dismiss()

    def update_groups_button(self):
        self.selected_group_id = None
        self.selected_category_id = None

        self.ids.groups_button.disabled = False
        self.ids.groups_button.text = 'Select Category Group'

        self.ids.categories_button.disabled = True
        self.ids.categories_button.text = 'No Category Group Selected'

    def update_categories_button(self):
        self.ids.categories_button.disabled = False
        self.ids.categories_button.text = 'Select Category'
        self.selected_category_id = None

    def open_groups_menu(self):
        groups = get_category_groups_by_type(self.get_transaction_type())
        if not groups:
            self.ids.groups_button.text = 'No Category Groups Created'
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
            caller=self.ids.groups_button,
            items=menu_items,
        )

        self.groups_menu.open()

    def select_group(self, group_id, group_name):
        self.update_categories_button()

        self.ids.groups_button.text = group_name
        self.selected_group_id = group_id
        self.groups_menu.dismiss()

    def open_categories_menu(self):
        categories = get_categories_by_group(self.selected_group_id)
        if not categories:
            self.ids.categories_button.text = 'No Category Created'
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
            caller=self.ids.categories_button,
            items=menu_items,
        )

        self.categories_menu.open()

    def select_category(self, category_id, category_name):
        self.ids.categories_button.text = category_name
        self.selected_category_id = category_id
        self.categories_menu.dismiss()

    def open_manage_category_screen(self):
        self.manager.current = 'categories'
        if hasattr(self, "groups_menu"):
            self.groups_menu.dismiss()
        if hasattr(self, "categories_menu"):
            self.categories_menu.dismiss()

    def set_current_date_time(self):
        now = datetime.now()
        self.ids.date_button.text = now.strftime('%Y-%m-%d')
        self.ids.time_button.text = now.strftime('%I:%M %p')

    def open_date_picker(self):
        date_picker = MDDatePicker()
        date_picker.open()
        date_picker.bind(on_save=self.set_date)
    
    def open_time_picker(self):
        time_picker = MDTimePicker()
        time_picker.open()
        time_picker.bind(on_save=self.set_time)

    def set_date(self, instance, value, date_range):
        self.ids.date_button.text = value.strftime('%Y-%m-%d')

    def set_time(self, instance, value):
        self.ids.time_button.text = value.strftime('%I:%M %p')

    def save_transaction(self):
        if not self.validate_form():
            return
        
        account = self.selected_account_id
        amount = float(self.amount)
        category = self.selected_category_id
        date = self.ids.date_button.text
        time = self.ids.time_button.text
        date_time = f"{date} {time}"
        notes = self.ids.notes_input.text

        insert_transaction(account, amount, category, date_time, notes)
        self.go_to_dashboard()

    def validate_form(self):

        if self.selected_account_id is None:
            print("Please select an account.")
            return False
        
        if float(self.amount) <= 0:
            print("Amount cannot be less than or equal to zero.")
            return False

        if self.get_transaction_type() is None:
            print("Please select a transaction type.")
            return False
        
        if self.selected_category_id is None:
            print("Please select a category.")
            return False

        return True