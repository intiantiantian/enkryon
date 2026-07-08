from kivy.uix.screenmanager import Screen

class DashboardScreen(Screen):

    def go_to_add_transaction(self):
        self.manager.current = 'add_transaction'

    def go_to_settings(self):
        self.manager.current = 'settings'

    def go_to_accounts(self):
        self.manager.current = 'accounts'

    def go_to_categories(self):
        self.manager.current = 'categories'

    def go_to_transactions(self):
        self.manager.current = 'transactions'