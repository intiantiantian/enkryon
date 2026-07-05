from kivy.uix.screenmanager import Screen

class AddTransactionScreen(Screen):
    
    def go_to_dashboard(self):
        self.manager.current = 'dashboard'