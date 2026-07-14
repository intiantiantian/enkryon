from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.utils import get_color_from_hex

from utils.snackbar import show_snackbar
from widgets.category_group_card import CategoryGroupCard

from database.category_group_repository import delete_category_group, get_category_groups_by_type, insert_category_group, update_category_group
from database.category_repository import insert_category, update_category, delete_category
from widgets.input_dialog import InputDialog

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
            active if transaction_type == 'income' else inactive
        )

        self.ids.expense_button.md_bg_color = (
            active if transaction_type == 'expense' else inactive
        )

        self.load_groups()

    def add_group(self):
        InputDialog(
            title="New Category Group",
            hint_text="Category Group name...",
            callback=self.save_group
        ).open()
        
    def save_group(self, group_name):
                   
        if not group_name:
            show_snackbar("Group name cannot be empty.")
            return
        
        success = insert_category_group(group_name, self.current_transaction_type)

        if success:
            show_snackbar(f"Group '{group_name}' added successfully.")
            self.load_groups()
        else:
            show_snackbar(f"Group name '{group_name}' already exists.")

    def rename_group(self, group_id, new_name):

        new_name = new_name.strip()

        if not new_name:
            show_snackbar("New group name cannot be empty.")
            return

        success = update_category_group(group_id, new_name)

        if success:
            show_snackbar(
                f"Group renamed to '{new_name}' successfully."
            )
            self.load_groups()
        else:
            show_snackbar(
                f"Group name '{new_name}' already exists."
            )
            show_snackbar(f"Group name '{new_name}' already exists.")

    def edit_group(self, group_id, group_name):
        InputDialog(
            title="Rename Group",
            hint_text="Group name...",
            text=group_name,
            callback=lambda name:
                self.rename_group(group_id, name)
        ).open()
    
    def perform_delete_group(self, group_id):
        self.close_delete_dialog()

        success, reason = delete_category_group(group_id)

        if success:
            show_snackbar("Group deleted successfully.")
            self.load_groups()
            return

        if reason == "has_categories":
            show_snackbar("Cannot delete group because it still contains categories.")
        else:
            show_snackbar("Group could not be deleted.")

    def confirm_delete_group(self, group_id):
        self.delete_dialog = MDDialog(
            title="Confirm Delete",
            text="Are you sure you want to delete this group? Groups with existing categories cannot be deleted.",            buttons=[
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

    def add_category(self, group_id):
        InputDialog(
            title="New Category",
            hint_text="Category name...",
            callback=lambda name: self.save_category(group_id, name)
        ).open()

    def save_category(self, group_id, category_name):
                   
        if not category_name:
            show_snackbar("Category name cannot be empty.")
            return
        
        success = insert_category(group_id, category_name)

        if success:
            show_snackbar(f"Category '{category_name}' added successfully.")
            self.load_groups()
        else:
            show_snackbar(f"Category name '{category_name}' already exists.")

    def rename_category(self, category_id, new_name):

        new_name = new_name.strip()

        if not new_name:
            show_snackbar("New category name cannot be empty.")
            return

        success = update_category(category_id, new_name)

        if success:
            show_snackbar(
                f"Category renamed to '{new_name}' successfully."
            )
            self.load_groups()
        else:
            show_snackbar(
                f"Category name '{new_name}' already exists."
            )

    def edit_category(self, category_id, category_name):
        InputDialog(
            title="Rename Category",
            hint_text="Category name...",
            text=category_name,
            callback=lambda name: self.rename_category(category_id, name)
        ).open()

    def perform_delete_category(self, category_id):
        self.close_delete_category_dialog()

        success, reason = delete_category(category_id)

        if success:
            show_snackbar("Category deleted successfully.")
            self.load_groups()
            return

        if reason == "referenced":
            show_snackbar("Cannot delete category because it has existing transactions.")
        else:
            show_snackbar("Category could not be deleted.")

    def confirm_delete_category(self, category_id):
        self.delete_category_dialog = MDDialog(
            title="Confirm Delete",
            text="Are you sure you want to delete this category? Categories with existing transactions cannot be deleted.",            buttons=[
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