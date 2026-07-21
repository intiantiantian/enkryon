from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from .action_results import render_action_result

from services.category_services import (
    create_category as create_category_workflow,
    create_group as create_group_workflow,
    get_groups_for_view,
    remove_category as remove_category_workflow,
    remove_group as remove_group_workflow,
    rename_category as rename_category_workflow,
    rename_group as rename_group_workflow,
)

from widgets.input_dialog import InputDialog
from widgets.category_group_card import CategoryGroupCard
from widgets.empty_state import EmptyState

class CategoriesScreen(Screen):
    
    return_screen = "dashboard"


    def go_back(self):
        destination = self.return_screen
        self.return_screen = "dashboard"
        self.manager.current = destination


    def on_pre_enter(self):
        self.rename_dialog = None
        self.rename_category_dialog = None
        self.delete_dialog = None
        self.delete_category_dialog = None

        self.current_transaction_type = 'income'
        self.ids.income_button.set_selected(self.current_transaction_type == 'income')
        self.ids.expense_button.set_selected(self.current_transaction_type == 'expense')

        self.expanded_groups = set()

        self.load_groups()


    def load_groups(self):
        self.ids.groups_container.clear_widgets()

        groups = get_groups_for_view(self.current_transaction_type)

        if not groups:
            label = (
                "income" if self.current_transaction_type == "income"
                else "expense"
            )

            self.ids.groups_container.add_widget(
                EmptyState(
                    icon="folder-outline",
                    title=f"No {label} category groups yet",
                    message="Tap + to create your first category group."
                )
            )
            return

        for group in groups:
            card = CategoryGroupCard()
            card.screen = self
            card.set_group(group)
            self.ids.groups_container.add_widget(card)

            if group.group_id in self.expanded_groups:
                card.toggle_group()


    def set_transaction_type(self, transaction_type):
        self.current_transaction_type = transaction_type

        self.ids.income_button.set_selected(transaction_type == 'income')
        self.ids.expense_button.set_selected(transaction_type == 'expense')

        self.load_groups()


    def add_group(self):
        InputDialog(
            title="New Category Group",
            hint_text="Category Group name...",
            callback=self.save_group
        ).open()
        

    def save_group(self, group_name):
        result = create_group_workflow(
            group_name,
            self.current_transaction_type,
        )
        render_action_result(
            result,
            refresh=self.load_groups,
            refresh_required=result.refresh_required,
        )


    def rename_group(self, group_id, new_name):
        result = rename_group_workflow(group_id, new_name)
        render_action_result(
            result,
            refresh=self.load_groups,
            refresh_required=result.refresh_required,
        )


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

        result = remove_group_workflow(group_id)
        render_action_result(
            result,
            refresh=self.load_groups,
            refresh_required=result.refresh_required,
        )


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
        result = create_category_workflow(group_id, category_name)
        render_action_result(
            result,
            refresh=self.load_groups,
            refresh_required=result.refresh_required,
        )


    def rename_category(self, category_id, new_name):
        result = rename_category_workflow(category_id, new_name)
        render_action_result(
            result,
            refresh=self.load_groups,
            refresh_required=result.refresh_required,
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

        result = remove_category_workflow(category_id)
        render_action_result(
            result,
            refresh=self.load_groups,
            refresh_required=result.refresh_required,
        )


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
