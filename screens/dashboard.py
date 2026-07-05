from kivy.uix.screenmanager import Screen

class DashboardScreen(Screen):

    def go_to_add_transaction(self):
        self.manager.current = 'add_transaction'

    def go_to_history(self):
        self.manager.current = 'history'

    def go_to_settings(self):
        self.manager.current = 'settings'