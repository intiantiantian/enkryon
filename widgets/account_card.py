from kivymd.uix.card import MDCard

class AccountCard(MDCard):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.account_id = None
    
    def set_account(self, account):
        self.ids.account_name.text = account[1]
        self.account_id = account[0]