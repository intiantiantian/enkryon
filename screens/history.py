from kivy.uix.screenmanager import Screen

class HistoryScreen(Screen):
    
    def go_to_dashboard(self):
        self.manager.current = 'dashboard'