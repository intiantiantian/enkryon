from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFillRoundFlatButton

from database.category_repository import get_categories_by_group

from widgets.category_card import CategoryCard

class CategoryGroupCard(MDCard):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.group_id = None
        self.expanded = False

    def set_group(self, group):
        self.group_id = group[0]
        self.ids.group_name.text = group[1]

    def edit_group(self):
        self.screen.open_rename_dialog(self.group_id, self.ids.group_name.text)

    def delete_group(self):
        self.screen.confirm_delete_group(self.group_id)

    def toggle_group(self):
        if self.expanded:
            self.ids.categories_container.clear_widgets()
            self.ids.toggle_button.icon = 'chevron-down'
            self.screen.expanded_groups.discard(self.group_id)
            self.expanded = False
            return
        
        categories = get_categories_by_group(self.group_id)

        for category in categories:
            card = CategoryCard()
            card.screen = self.screen
            card.group_card = self
            card.set_category(category)
            self.ids.categories_container.add_widget(card)

        self.category_name_input = MDTextField(hint_text='Category Name')
        self.add_category_button = MDFillRoundFlatButton(text='+ Add New Category')
        self.add_category_button.bind(on_release=lambda x: self.add_category())

        self.ids.categories_container.add_widget(self.category_name_input)
        self.ids.categories_container.add_widget(self.add_category_button)

        self.ids.toggle_button.icon = 'chevron-up'
        self.screen.expanded_groups.add(self.group_id)
        self.expanded = True

    def add_category(self):
        self.screen.add_category(
            self.group_id,
            self.category_name_input.text
        )