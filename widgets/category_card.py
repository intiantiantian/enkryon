from kivymd.uix.card import MDCard

class CategoryCard(MDCard):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.category_id = None
        self.group_card = None
    
    def set_category(self, category):
        self.ids.category_name.text = category[2]
        self.category_id = category[0]

    def edit_category(self):
        self.screen.open_rename_category_dialog(self.category_id, self.ids.category_name.text)

    def delete_category(self):
        self.screen.confirm_delete_category(self.category_id)