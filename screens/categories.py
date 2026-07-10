from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton
from kivy.utils import get_color_from_hex

from utils.snackbar import show_snackbar
from widgets.category_group_card import CategoryGroupCard

from database.category_group_repository import delete_category_group, get_category_groups_by_type, insert_category_group, update_category_group
from database.category_repository import insert_category, update_category, delete_category

class CategoriesScreen(Screen):
    
    def go_to_dashboard(self):
        self.manager.current = 'dashboard'

    def on_pre_enter(self):
        self.rename_dialog = None
        self.rename_category_dialog = None
        self.delete_dialog = None
        self.delete_category_dialog = None

        self.current_transaction_type = 'income'
        self.ids.income_button.md_bg_color = get_color_from_hex("#D5F4BE")
        self.ids.expense_button.md_bg_color = get_color_from_hex("#FFFFFF")

        self.expanded_groups = set()

        self.load_groups()

    def load_groups(self):
        self.ids.groups_container.clear_widgets()

        for group in get_category_groups_by_type(self.current_transaction_type):
            card = CategoryGroupCard()
            card.screen = self
            card.set_group(group)
            self.ids.groups_container.add_widget(card)

            if group[0] in self.expanded_groups:
                card.toggle_group()

    def set_transaction_type(self, transaction_type):
        self.current_transaction_type = transaction_type

        active = get_color_from_hex('#D5F4BE')
        inactive = get_color_from_hex("#FFFFFF")

        self.ids.income_button.md_bg_color = (
            active if transaction_type is 'income' else inactive
        )

        self.ids.expense_button.md_bg_color = (
            active if transaction_type == 'expense' else inactive
        )

        self.load_groups()

    def add_group(self):
        group_name = self.ids.group_name_input.text.strip()
        if not group_name:
            show_snackbar("Group name cannot be empty.")
            return
        
        success = insert_category_group(group_name, self.current_transaction_type)

        if success:
            show_snackbar(f"Group '{group_name}' added successfully.")
            self.ids.group_name_input.text = ''
            self.load_groups()
        else:
            show_snackbar(f"Group name '{group_name}' already exists.")

    def open_rename_dialog(self, group_id, group_name):

        if self.rename_dialog:
            self.rename_dialog.dismiss()
        
        self.rename_dialog = MDDialog(
            title="Rename Group",
            type="custom",
            content_cls=MDTextField(
                text=group_name,
                multiline=False
            ),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=self.close_rename_dialog
                ),
                MDFlatButton(
                    text="RENAME",
                    on_release=lambda x: self.rename_group(group_id)
                )
            ]
        )
        self.rename_dialog.open()

    def close_rename_dialog(self, *args):
        self.rename_dialog.dismiss()
        self.rename_dialog = None

    def rename_group(self, group_id):

        new_name = self.rename_dialog.content_cls.text.strip()
        if not new_name:
            show_snackbar("New group name cannot be empty")
            return
        
        success = update_category_group(group_id, new_name)

        if success:
            show_snackbar(f"Group renamed to '{new_name}' successfully.")
            self.close_rename_dialog()
            self.load_groups()
        else:
            show_snackbar(f"Group name '{new_name}' already exists.")

    def perform_delete_group(self, group_id):
        self.close_delete_dialog()
        success = delete_category_group(group_id)

        if success:
            show_snackbar(f"Group deleted successfully.")
            self.load_groups()
        else:
            show_snackbar(f"Unable to delete group.")

    def confirm_delete_group(self, group_id):
        self.delete_dialog = MDDialog(
            title="Confirm Delete",
            text="Are you sure you want to delete this group?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=self.close_delete_dialog
                ),
                MDFlatButton(
                    text="DELETE",
                    on_release=lambda x: self.perform_delete_group(group_id)
                )
            ]
        )
        self.delete_dialog.open()

    def close_delete_dialog(self, *args):
        if self.delete_dialog:
            self.delete_dialog.dismiss()
            self.delete_dialog = None

    def add_category(self, group_id, category_name):
        category_name = category_name.strip()

        if not category_name:
            show_snackbar("Category name cannot be empty.")
            return
        
        success = insert_category(group_id, category_name)

        if success:
            show_snackbar(f"Category '{category_name}' added successfully.")
            self.load_groups()
        else:
            show_snackbar(f"Category name '{category_name}' already exists.")

    def open_rename_category_dialog(self, category_id, category_name):
        if self.rename_category_dialog:
            self.rename_category_dialog.dismiss()
        
        self.rename_category_dialog = MDDialog(
            title="Rename Category",
            type="custom",
            content_cls=MDTextField(
                text=category_name,
                multiline=False
            ),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=self.close_rename_category_dialog
                ),
                MDFlatButton(
                    text="RENAME",
                    on_release=lambda x: self.rename_category(category_id)
                )
            ]
        )
        self.rename_category_dialog.open()

    def close_rename_category_dialog(self, *args):
        self.rename_category_dialog.dismiss()
        self.rename_category_dialog = None

    def rename_category(self, category_id):
        new_name = self.rename_category_dialog.content_cls.text.strip()
        if not new_name:
            show_snackbar("New category name cannot be empty")
            return
        
        success = update_category(category_id, new_name)

        if success:
            show_snackbar(f"Category renamed to '{new_name}' successfully.")
            self.close_rename_category_dialog()
            self.load_groups()
        else:
            show_snackbar(f"Category name '{new_name}' already exists.")

    def perform_delete_category(self, category_id):
        self.close_delete_category_dialog()
        success = delete_category(category_id)

        if success:
            show_snackbar("Category deleted successfully.")
            self.load_groups()
        else:
            show_snackbar("Unable to delete category.")

    def confirm_delete_category(self, category_id):
        self.delete_category_dialog = MDDialog(
            title="Confirm Delete",
            text="Are you sure you want to delete this category?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=self.close_delete_category_dialog
                ),
                MDFlatButton(
                    text="DELETE",
                    on_release=lambda x: self.perform_delete_category(category_id)
                )
            ]
        )
        self.delete_category_dialog.open()

    def close_delete_category_dialog(self, *args):
        if self.delete_category_dialog:
            self.delete_category_dialog.dismiss()
            self.delete_category_dialog = None