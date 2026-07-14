from kivymd.uix.card import MDCard

from database.category_repository import get_categories_by_group

from widgets.category_card import CategoryCard
from widgets.empty_state import EmptyState

class CategoryGroupCard(MDCard):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.group_id = None
        self.expanded = False

    def set_group(self, group):
        self.group_id = group[0]
        self.ids.group_name.text = group[1]

    def edit_group(self):
        self.screen.edit_group(
            self.group_id,
            self.ids.group_name.text
        )

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

        if not categories:
            self.ids.categories_container.add_widget(
                EmptyState(
                    title="No categories yet",
                    message="Tap + to add a category to this group."
                )
            )
        else:
            for category in categories:
                card = CategoryCard()
                card.screen = self.screen
                card.group_card = self
                card.set_category(category)
                self.ids.categories_container.add_widget(card)

        self.ids.toggle_button.icon = 'chevron-up'
        self.screen.expanded_groups.add(self.group_id)
        self.expanded = True

    def add_category(self):
        self.screen.add_category(self.group_id)